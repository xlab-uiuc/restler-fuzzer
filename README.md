# RESTler

## Intro

If you want to know what RESTler is and how to install it, see [RESTler setup](./docs/user-guide/Setup.md).

This doc assumes basic knowledge about RESTler and focuses directly on how to set up RESler with a cloud service. We will take Azure Storage as an example cloud service.

## How to compile swagger specs?

Pass the swagger specification file path to the RESTler compile command:
```
./Restler compile --api_spec ../swagger.json
```

This command creates a new sub-directory **Compile** where the results of the compilation are saved in several files:
- _grammar.py_ and _grammar.json_ are the RESTler grammars
- _dict.json_ is a default dictionary associating parameters types with a set of default values (you can edit this file if you want more or different valrkdownues)
- _engine_settings.json_ is a default engine_settings file with options for the RESTler test engine (you can edit this file to turn on other options)
- _config.json_ is a default compiler configuration file (you can edit this file and re-run the compiler with other options)

### Custom Values

Before running the tests, you might need to make a few edits in the dict.json file to define custom values for some parameters and headers (depends on the endpoints being tested).

For Azure Storage control plane APIs, you must define "subscriptionId", "resourceGroupName", "accountName”, etc according to your Azure account, otherwise, the request will always fail as a Bad Request. An example endpoint is given below:

`/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Storage/storageAccounts/{accountName}/blobServices/default/containers/{containerName}/immutabilityPolicies/{immutabilityPolicyName}`


Before directly making these changes to the Compile/dict.json file. The following method is recommended:
- Copy the config.json and dict.json (and possibly engine_settings.json if you need to modify them) out of this Compile folder.
- Change the dictionary as needed.
- Change the config.json path to the dictionary (CustomDictionaryFilePath) to the dictionary you copied and modified in step (2).
- Run the compile command that takes a configuration file as input, restler.exe compile config.json, using the config.json modified in step (3). Once you have compiled with the new property, you can add new values to be fuzzed without having to re-compile again.

**Note:** Include custom value for api_version in dict.json (mandatory).
<br/>

<br/>

## How to setup up authentication (to use Azure APIs)?



To use azure APIs we need authentication tokens. There are three ways to authorize access to data in Azure Storage:
- Shared Key
- Shared Access Signature
- Azure AD

We use Azure AD method to get access tokens which are used to authorize requests (we faced issues in automating the other two methods with RESTler e.g., issue for [Shared Key](https://github.com/microsoft/restler-fuzzer/issues/396#issue-1043943222)). These tokens are typically valid for 50 minutes. RESTler expects users to provide a separate python program to generate these auth tokens when running tests with RESTler. This script is invoked in a separate process by RESTler to obtain and regularly refresh tokens. RESTler will obtain new tokens by invoking the token generation script with the frequency specified in the --token_refresh_interval option.

For Azure Storage, the auth token generation script can be found under [scripts](./scripts/auth_token.py).
To run RESTler fuzz mode with this script run the following command:
```
./Restler fuzz --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json --token_refresh_command "python /path/to/token_script.py" --token_refresh_interval 100
```
<br/>



## What if you want to run the same test (same sequences and fuzzed values) with two services?

RESTler does not support this feature. However, we have implemented a workaround.

Run a test/fuzz/fuzz-lean with the first service. When it completes, pass the network logs path to the script `extract_requests.py` in the [scripts](./scripts) folder.
```bash
python scripts/extract_requests.py path/to/network_logs
```
This script will extract all the full requests made during the test (includes the fuzzed values) and formats it in `all_reqs_replay.txt`. These requests can be tested with another service using the **replay** mode of RESTler.
```
./Restler replay --replay_log all_reqs_replay.txt --token_refresh_command "python /path/to/token_script.py" --token_refresh_interval 100
```

After the replay is complete, locate network logs in the **replay** directory. All the requests and their responses can be found in these logs.

To summarise the results, run **Restler.RequestsAnalyzer**.

**Note:** Before running, open the network logs and add the following line (newline) after the Authorization token line:
```Generation-1: Rendering Sequence-1```

To run the analyzer, run:

```
./Restler.ResultsAnalyzer analyze replay/path/to/network_logs --output_dir .
```

This will generate runSummary.json and errorBucket.json. 