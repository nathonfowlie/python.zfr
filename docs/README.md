# ZFR

Command-line utility to perform test case management using Zephyr Scale for Jira.

The intention is that this would be consumed by other scripts to automate the
generate of test plans/cycles/executions, and publishing test results back to
Zephyr. Hence why all of the output is in JSON format, as this makes it easier
to pass the Zephyr objects to another script, or write them to file for further
processing by another tool.

## Usage

### Managing Zephyr Folders

```shell
# outputs the created folder in JSON format.
$ zfr-folder create --name foo
{"id": 11, "name": "/foo", "type": "TEST_PLAN"}

# outputs the updated folder in JSON format.
$ zfr-folder update --id 11 --name bar
{"id": "11", "name": "/bar", "type": "TEST_PLAN"}
```

### Managing Test Plans

```shell
# outputs the created test plan in JSON format.
$ zfr-plan create --project PZ --name "Some Plan" --labels a,b,c --objective "Test all the things" --folder bar
{"attachments": [], "comments": [], "created_by": "JIRAUSER10000", "created_on": "2021-09-23T16:18:52.862Z", "custom_fields": {}, "folder": "/bar", "issue_links": [], "key": "PZ-P12", "labels": ["a", "b", "c"], "name": "Some Plan", "objective": "Test all the things", "owner": "", "project_key": "PZ", "status": "Draft", "test_runs": [], "updated_by": "", "updated_on": null}

# outputs the updated test plan in JSON format.
$ zfr-plan update --project PZ --key PZ-P12 --objective "Test some of the things."
{"attachments": [], "comments": [], "created_by": "JIRAUSER10000", "created_on": "2021-09-23T16:18:52.862Z", "custom_fields": {}, "folder": "/bar", "issue_links": [], "key": "PZ-P12", "labels": ["a", "b", "c"], "name": "Some Plan", "objective": "Test all the things", "owner": "", "project_key": "PZ", "status": "Draft", "test_runs": [], "updated_by": "", "updated_on": null}

# outputs the retrieve test plan in JSON format.
$ zfr-plan get --key PZ-P12
{"attachments": [], "comments": [], "created_by": "JIRAUSER10000", "created_on": "2021-09-23T16:18:52.862Z", "custom_fields": {}, "folder": "/bar", "issue_links": [], "key": "PZ-P12", "labels": ["a", "b", "c"], "name": "Some Plan", "objective": "Test some of the things.", "owner": "", "project_key": "PZ", "status": "Draft", "test_runs": [], "updated_by": "JIRAUSER10000", "updated_on": "2021-09-23T16:19:49.796Z"}

# outputs the deleted test plan in JSON format.
$ zfr-plan delete --key PZ-P12
{"attachments": [], "comments": [], "created_by": "JIRAUSER10000", "created_on": "2021-09-23T16:18:52.862Z", "custom_fields": {}, "folder": "/bar", "issue_links": [], "key": "PZ-P12", "labels": ["a", "b", "c"], "name": "Some Plan", "objective": "Test some of the things.", "owner": "", "project_key": "PZ", "status": "Draft", "test_runs": [], "updated_by": "JIRAUSER10000", "updated_on": "2021-09-23T16:19:49.796Z"}
```

### Authentication

Authentication credentials and the Jira URL can be passed as cli argument, as environment variables, or stored in a configuration file.

#### CLI Arguments

- --url
- --username
- --password

#### Environment Variables

- ZFR_URL
- ZFR_USERNAME
- ZFR_PASSWORD

#### Configuration File

The default location is ```$HOME/zfr.cfg```, but a different location can be specified via the ```--config``` cli argument.

The configuration is in ini format, and should contain the following entries:

```ini
[jira]
url=https://some_url
user=some_user
password=some_password
```

## Development Environment

1. Install PodMan.

    ```shell
    . /etc/os-release
    sudo sh -c "echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/x${NAME}_${VERSION_ID}/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list"
    wget -nv https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/x${NAME}_${VERSION_ID}/Release.key -O Release.key
    sudo apt-key add - < Release.key
    sudo apt-get update -qq
    sudo apt-get -qq -y install podman
    sudo mkdir -p /etc/containers
    echo -e "[registries.search]\nregistries = ['docker.io', 'quay.io']" | sudo tee /etc/containers/registries.conf
    podman info
    sudo vim  /home/lordgoofus/.config/containers/storage.conf
    events_logger = "file"
    ```

2. Create data volumes to persist jira data

    ```shell
    docker volume create --name postgresVolume
    docker volume create --name jiraVolume
    ```

3. Create a pod for the jira application + db.

    ```shell
    podman pod create --name jira-pod --publish 8080:8080
    ```

4. Add the Jira & Postgres containers to the pod

    ```shell
    podman run -v postgresVolume:/var/lib/postgresql/data --name="jiradb" -dt -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=jira --rm --pod jira-pod docker.io/library/postgres:13.4-alpine
    podman run -v jiraVolume:/var/atlassian/application-data/jira --name="jira-app" -dt --rm --pod jira-pod -e ATL_JDBC_URL=jdbc:postgresql://localhost:5432/jira -e ATL_JDBC_USER=user -e ATL_JDBC_PASSWORD=password -e ATL_DB_DRIVER=org.postgresql.Driver -e ATL_DB_TYPE=postgres72 atlassian/jira-software:8.17.0-jdk11
    ```

5. Find the IP assigned to the pod.

    ```shell
    ip addr | grep 172 to get the IP
    ```

6. Navigate to ```http://<ip>:8080``` and follow the setup wizard.

7. Create a new project called ```Python Zephyr```.

8. Install Zephyr Scale - Test Management for Jira.

9. Update Jira/all the applications.

10. Enable Zephyr Scale for the Python Zephyr project.

11. Clone the repo, and from the repository root run ```make configure && make requirements```.

12. Run ```make dev-install``` to install an editable version of the package.

13. If all went well, should be able to run the utility now.