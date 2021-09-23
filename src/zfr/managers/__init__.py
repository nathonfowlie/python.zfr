"""Helper classes used to manage Zephyr Scale test configurations."""

from dataclasses import asdict
from http import HTTPStatus
from requests import Response
from requests_toolbelt import sessions
from typing import Dict, List, Optional
from urllib3.util.retry import Retry
from zfr.dataobjects.folder import Folder, FolderCreate, FolderType
from zfr.dataobjects.plan import Attachment, Plan, PlanCreate, PlanUpdate
from zfr.exception import AuthorizationError
from zfr.utils import dict_to_camel, dict_to_snake, TimeoutHTTPAdapter


class FolderManager:
    """Manage Zephyr Scale folders."""

    def __init__(self, url: str, api_suffix: str, username: str, password: str) -> None:
        """Initialize a new FolderManager object.

        Args:
            url: Jira URL.
            api_suffix: Content path used to access the Zephyr Scale REST API.
            username: Username used to make authenticated API calls.
            password: Password used to make authenticated API calls.
        """
        self._url = url
        self._api_suffix = api_suffix

        # Set a base url, auth credentials, a retry strategy, request timeout
        # value, and add a single handler for all authentication/internal 
        # server errors so we don't need to keep passing the same information
        # all over the place.
        self._session = sessions.BaseUrlSession(base_url=url)
        self._session.auth = (username, password)
        self._session.hooks['response'] = self._response_hook

        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )

        self._session.mount('https://', TimeoutHTTPAdapter(max_retries=retries, timeout=90))

    def create(self, folder: FolderCreate) -> Folder:
        """Create a new folder.

        Args:
            folder: Folder to be created.

        Returns:
            The created folder.

        Raises:
            AuthorizationError: If the client does not have permission to
                create folders.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Folder][zfr.dataobjects.folder.Folder]
        """
        result: Optional[Folder] = None
        endpoint = f"/{self._api_suffix}/folder"

        data = dict_to_camel(asdict(folder))

        # zephyr requires the folder name to start with a forward slash when
        # creating folders, but NOT start with a forward slash when updating
        # a folder. We manage the inconsistency here to make things easier for
        # users.
        if not data['name'].startswith('/'):
            data['name'] = f"/{data['name']}"

        print(data)

        resp = self._session.post(endpoint, json=data)

        if resp.status_code == HTTPStatus.CREATED:
            resp_data = resp.json()
            result = Folder(
                id=resp_data['id'],
                name=folder.name.lstrip('/'),
                type=folder.type
            )
        elif resp.status_code == HTTPStatus.BAD_REQUEST:
            resp_data = resp.json()
            raise RuntimeError(', '.join(resp_data['errorMessages']))

        return result

    def update(self, folder: Folder) -> Folder:
        """Update an existing folder.

        Args:
            folder: The modified folder.

        Returns:
            The updated Folder.

        Raises:
            AuthorizationError: If the client does not have permission to
                modify folders.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Folder][zfr.dataobjects.folder.Folder]
        """
        endpoint = f"/{self._api_suffix}/folder/{folder.id}"

        data = dict_to_camel(asdict(folder))
        data['name'] = data['name'].lstrip('/')
        data.pop('id')
        data.pop('type')

        # remove any null attributes so we don't delete existing data
        new_dict = {key: value for key, value in data.items() if value}

        resp = self._session.put(endpoint, json=new_dict)

        if resp.status_code == HTTPStatus.OK:
            return folder
        elif resp.status_code == HTTPStatus.BAD_REQUEST:
            resp_data = resp.json()
            raise RuntimeError(', '.join(resp_data['errorMessages']))


    def _response_hook(self, response, *args, **kwargs) -> None:
        """Request hook used to centrally manage handle HTTP errors.

        This is used to response to authoriation or server-side errors
        in one place, to avoid code duplication and ensure consistent
        error handling behaviour.

        Args:
            response: HTTP response recieved from the remote host.
            args: HTTP response arguments.
            kwargs: Additional custom args.
        """
        if response.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
            raise AuthorizationError(f'Client does not have permission to perform this action. {response.request.method} {response.request.url}')
        elif response.status_code > HTTPStatus.FORBIDDEN:
            err_msg = (
                'Unexpected response recieved from the remote server '
                f'{response.status_code} {response.request.method} '
                f'{response.request.url} {response.text}'
            )
            raise RuntimeError(err_msg)


class PlanManager:
    """Manage test plans."""

    def __init__(self, url: str, api_suffix: str, username: str, password: str) -> None:
        """Initialize a PlanManager object.

        Args:
            url: Jira URL.
            api_suffix: Content path used to access the Zephyr Scale REST API.
            username: Username used to make authenticated API calls.
            password: Password used to make authenticated API calls.
        """
        self._url = url
        self._api_suffix = api_suffix

        # Set a base url, auth credentials, a retry strategy, request timeout
        # value, and add a single handler for all authentication/internal 
        # server errors so we don't need to keep passing the same information
        # all over the place.
        self._session = sessions.BaseUrlSession(base_url=url)
        self._session.auth = (username, password)
        self._session.hooks['response'] = self._response_hook

        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )

        self._session.mount('https://', TimeoutHTTPAdapter(max_retries=retries, timeout=90))

    def create(self, plan: PlanCreate) -> Optional[Plan]:
        """Create a new test plan.

        Args:
            plan: The plan to be created.

        Returns:
            The newly created plan.

        Raises:
            AuthorizationError: If the client does not have permission to
                create plans.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        result: Optional[Plan] = None

        # The Zephyr API will throw an error if you try to assign a
        # non-existent folder to a plan, so we try to catch it, create
        # the missing folder, then re-attempt to create the plan before
        # giving up.

        resp = self._create_plan(plan)

        if resp.status_code == HTTPStatus.CREATED:
            resp_data = resp.json()
            result = self.get(resp_data['key'])
        elif resp.status_code == HTTPStatus.BAD_REQUEST:
            result = self._handle_creation_error(plan, resp.json())
            if not result:
                raise RuntimeError(f"Failed to create  plan {plan.name}")

        # If the plan was created, upload the attachments, and retrieve the
        # plan again to get the updated metadata containing the attachment
        # identifiers.
        if result and plan.attachments:
            self._upload_attachments(result.key, plan.attachments)
            result = self.get(result.key)

        return result

    def delete(self, key: str) -> Optional[Plan]:
        """Delete an existing test plan.

        Args:
            key: The plan to be deleted.

        Returns:
            Details of the deleted plan.

        Raises:
            AuthorizationError: If the client does not have permission to
                delete plans.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        # exit early if the plan doesn't exist. Avoids making un-necessary
        # api calls.
        result: Optional[Plan] = self.get(key)
        if not result:
            return None

        endpoint = f"/{self._api_suffix}/testplan/{key}"

        resp = self._session.delete(endpoint)

        if resp.status_code == HTTPStatus.NO_CONTENT or resp.status_code == HTTPStatus.NOT_FOUND:
            return result

    def get(self, key: str, fields: Optional[List[str]] = None) -> Optional[Plan]:
        """Get an existing plan.

        Args:
            key: The plan to be retrieved.
            fields: Optionally limit the fieldsto be retrieved, to improve performance.

        Raises:
            AuthorizationError: If the client does not have permission to
                retrieve plans.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        result = None

        endpoint = f"{self._api_suffix}/testplan/{key}"
        if fields:
            endpoint += f"?fields={','.join(fields)}"
                
        resp = self._session.get(endpoint)        

        if resp.status_code == HTTPStatus.OK:
            resp_data = dict_to_snake(resp.json())            
            result = Plan(**resp_data)
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            result = None

        # If the plan was created, upload the attachments, and retrieve the
        # plan again to get the updated metadata containing the attachment
        # identifiers.
        if result:
            result.attachments = self.get_attachments(result.key)

        return result

    def get_attachments(self, key: str) -> Optional[List[Attachment]]:
        """Get the list of file attachments on an existing plan.

        Args:
            key: Plan key.

        Returns:
           A list of attachments associated with the plan, or ```None``` if a
           plan with the given key could not be found.

        Raises:
            AuthorizationError: If the client does not have permission to
                retrieve attachments.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Attachment][zfr.dataobjects.Attachment]
        """
        result: Optional[List[Attachment]] = []

        endpoint = f"{self._api_suffix}/testplan/{key}/attachments"

        resp = self._session.get(endpoint)

        if resp.status_code == HTTPStatus.OK:
            resp_data = dict_to_snake(resp.json())
            result = [Attachment(**x) for x in resp_data]
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            result = None
        
        return result

    def update(self, plan: PlanUpdate) -> Optional[Plan]:
        """Update an existing plan.

        Args:
            plan: The modified plan.

        Returns:
           The updated plan, or None if a plan with a matching key could not
           be found.

        Raises:
            AuthorizationError: If the client does not have permission to
                modify plans.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        result: Optional[Plan] = self.get(plan.key)
        if not result:
            raise RuntimeError(f"No such plan - {plan.key}.")

        # The Zephyr API will throw an error if you try to assign a
        # non-existent folder to a plan, so we try to catch it, create
        # the missing folder, then re-attempt to create the plan before
        # giving up.
        resp = self._update_plan(plan)

        if resp.status_code == HTTPStatus.OK:
            result = result
        elif resp.status_code == HTTPStatus.BAD_REQUEST:
            result = self._handle_update_error(result.project_key, plan, resp.json())
            if not result:
                raise RuntimeError(f"Failed to update {plan.name}.")

        # If the plan was created, upload the attachments, and retrieve the
        # plan again to get the updated metadata containing the attachment
        # identifiers.
        if result and plan.attachments:
            self._upload_attachments(plan.key, plan.attachments)
            result = self.get(result.key)

        return result

    def _create_folder(self, folder: FolderCreate) -> Optional[Folder]:
        """Create a new folder for logically grouping test plans.

        Args:
            folder: The folder to be created.

        Returns:
            A Folder object containing the folder configuration details.

        Raises:
            AuthorizationError: If the client does not have permission to
                create folders.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Folder][zfr.dataobjects.plan.Folder]
        """
        result: Optional[Folder] = None

        folder_dict = dict_to_camel(asdict(folder))

        # zephyr requires the folder name to start with a forward slash when
        # creating folders, but NOT start with a forward slash when updating
        # a folder. We manage the inconsistency here to make things easier for
        # users.
        if not folder_dict['name'].startswith('/'):
            folder_dict['name'] = f"/{folder_dict['name']}"

        endpoint = f"{self._api_suffix}/folder"

        resp = self._session.post(endpoint, json=folder_dict)

        if resp.status_code == HTTPStatus.CREATED:
            resp_data = resp.json()
            result = Folder(
                id=resp_data['id'],
                name=folder.name,
                type=folder.type
            )
        elif resp.status_code == HTTPStatus.BAD_REQUEST:
            resp_data = resp.json()
            raise RuntimeError(', '.join(resp_data['errorMessages']))

        return result

    def _create_plan(self, plan: PlanCreate) -> Response:
        """Create a new plan.

        Args:
            plan: The plan to be created.

        Returns:
            A Response object with details of whether the plan creation was
            successful or not.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        plan_dict = dict_to_camel(asdict(plan))

        if 'attachments' in plan_dict:
            plan_dict.pop('attachments')

        if plan_dict['folder'] and not plan_dict['folder'].startswith('/'):
            plan_dict['folder'] = f"/{plan_dict['folder']}"

        endpoint = f"{self._api_suffix}/testplan/"
        return self._session.post(endpoint, json=plan_dict)

    def _handle_creation_error(self, plan: PlanCreate, resp_data: Dict) -> Optional[Plan]:
        """Attempt to gracefully handle errors when create a new plan.

        Args:
            plan: Plan to be created.
            resp_data: HTTP response object containing the error details.

        Returns:
            A Response object with details of whether the plan creation was
            successful or not.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        result: Optional[Plan] = None

        if any("was not found for field folder" in x for x in resp_data['errorMessages']):
            new_folder = FolderCreate(
                project_key=plan.project_key,
                name=plan.folder,
                type=FolderType.PLAN
            )
            created_folder: Optional[Folder] = self._create_folder(new_folder)

            if created_folder:
                result = self.create(plan)

        return result

    def _handle_update_error(self, project_key: str, plan: PlanUpdate, resp_data: Dict) -> Optional[Plan]:
        """Attempt to gracefully handle errors when updating an existing plan.

        Args:
            project_key: Project that the plan belongs to.
            plan: The modified Plan.
            resp_data: HTTP response object containing the error details.

        Returns:
            A Response object with details of whether the plan was successfully
            updated.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        result: Optional[Plan] = None

        if any("was not found for field folder" in x for x in resp_data['errorMessages']):
            new_folder = FolderCreate(
                project_key=project_key,
                name=plan.folder,
                type=FolderType.PLAN
            )
            created_folder: Optional[Folder] = self._create_folder(new_folder)

            if created_folder:
                result = self.update(plan)

        return result

    def _response_hook(self, response, *args, **kwargs) -> None:
        """Request hook used to centrally manage handle HTTP errors.

        This is used to response to authoriation or server-side errors
        in one place, to avoid code duplication and ensure consistent
        error handling behaviour.

        Args:
            response: HTTP response recieved from the remote host.
            args: HTTP response arguments.
            kwargs: Additional custom args.
        """
        if response.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
            raise AuthorizationError(f'Client does not have permission to perform this action. {response.request.method} {response.request.url}')
        elif response.status_code > HTTPStatus.FORBIDDEN:
            err_msg = (
                'Unexpected response recieved from the remote server '
                f'{response.status_code} {response.request.method} '
                f'{response.request.url} {response.text}'
            )
            raise RuntimeError(err_msg)

    def _update_plan(self, plan: PlanUpdate) -> Response:
        """Update an existing plan.

        Args:
            plan: The modified plan.

        Returns:
            A Response object with details of whether the plan was successfully
            updated.

        _See Also_:
            [Plan][zfr.dataobjects.plan.Plan]
        """
        existing: Optional[Plan] = self.get(plan.key)

        if not existing:
            raise RuntimeError(f"No such plan - {plan.key}.")

        # get the status from the existing plan if it wasn't changed.
        if not plan.status:
            plan.status = existing.status

        plan_dict = dict_to_camel(asdict(plan))

        # to make it easier to work with Zephyr, the data object has some
        # additional properties that aren't used by the REST API, so we
        # need to remove them prior to calling the update endpoint.
        remove_keys = ['key', 'attachments']
        for key in remove_keys:
            plan_dict.pop(key)

        # fix inconsistency with the way the Zephyr Scale API handles folder
        # names
        if plan_dict['folder'] and not plan_dict['folder'].startswith('/'):
            plan_dict['folder'] = f"/{plan_dict['folder']}"

        # remove empty fields so we don't accidentally over-write data
        new_dict = {key: value for key, value in plan_dict.items() if value}

        endpoint = f"{self._api_suffix}/testplan/{plan.key}"

        resp = self._session.put(endpoint, json=new_dict)

        return resp

    def _upload_attachments(self, key: str, attachments: List[str]) -> None:
        """Upload one or more attachments to a test plan.

        Args:
            key: Plan key (eg: MYPROJECT-P123).
            attachments: List of attachments to be uploaded.

        Raises:
            AuthorizationError: If the client does not have permission to
                create folders.
            RuntimeError: If the Zephyr API returns an unexpected error.

        _See Also_:
            [Attachment][zfr.dataobjects.Attachment]
        """
        endpoint = f"{self._api_suffix}/testplan/{key}/attachments"

        for attachment in attachments:
            with open(attachment, 'rb') as infile:
                upload_data = {'file': infile}

                resp = self._session.post(endpoint, files=upload_data)

                if resp.status_code != HTTPStatus.CREATED:
                    err_msg = (
                        f"Recieved HTTP response {resp.status_code} "
                        f"attaching {attachment} to {key}."
                    )
                    raise RuntimeError(err_msg)
