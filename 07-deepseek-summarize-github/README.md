# Develop with DeepSeek R1 on local GPUs, deploy with serverless inference

In this example we will develop a Tower app that uses the Deepseek R1 model to analyze a GitHub issue and its comments and proposes the best course of action to address the issue. While developing and debugging, we will use the local GPUs of the dev machine for inference. Once we move the app to a production environment, we will use a serverless inference provider. 
 
This example demonstrates the local development and cloud deployment capabilities of Tower:
- It uses Tower's --local mode to run the app on your dev machine  
- You can use local GPUs (e.g. Apple Silicon) to save on inference costs during development and avoid inference rate throttling
- Once you are done developing your app, you can deploy the app to the Tower cloud

The example also shows the flexibility of integrations that are possible with Tower:
- You can use ollama to host a local inference server that the Tower app will use in local mode
- You can use Together.AI as the serverless inference provider
- To maintain flexibility with inference providers, we will use Hugging Face Hub as the router of inference calls


## Set Up Inference Providers
Here, you will set up local and serverless inference providers. Tower does not typically require this step, but in our example we will use these inference providers to demonstrate local inference capabilities. 

### Install ollama and a small Deepseek R1 model

During development we will use [`ollama`](https://ollama.com/) to serve as a local inference server.

```
pip install ollama
ollama pull deepseek-r1:14b
```

### Sign Up for Hugging Face  

In production, we will use Hugging Face Hub to route our inference calls. You don't have to use the Hub and you can call inference providers directly, but using the Hub is free, and it adds flexibility to being able to switch providers that provide you better value, e.g. have lower latency, higher request rates, lower costs, better availability etc.

You should [sign up for Hugging Face](https://huggingface.co/join) and get the Hugging Face [access token](https://huggingface.co/docs/hub/en/security-tokens). Note this token as you will need it later. 

### Install Hugging Face Hub

```
pip install huggingface_hub>=0.34.3
```

### Sign Up for Together.ai

In this example we use Together.ai as our serverless inference provider for the full Deepseek R1 model. Sign up for [together.ai](https://www.together.ai/) and note its [access key](https://docs.together.ai/reference/authentication-1). 

### Enable Together.ai in Hugging Face Hub

Follow this [quickstart](https://docs.together.ai/docs/quickstart-using-hugging-face-inference) to enable Together.ai in the Hugging Face Hub. You will enter your Together.ai access token in the Hugging Face Hub settings. Once you do that, you can use your Hugging Face access token to make inference calls from your Tower app. 

## Set up Tower

Go through the Tower [Quickstart](https://docs.tower.dev/docs/getting-started/quick-start) guide, if you haven't already.


## Deploy the app to Tower

In terminal, type this command to deploy the app to Tower

```bash
tower deploy
```


## Creating app secrets

Secrets in Tower are environment variables that will automatically be passed to your app.

The following secrets need to be defined in Tower's environments:

* `TOWER_INFERENCE_ROUTER` - can be set to "ollama" or "hugging_face_hub" when running the app in local mode. Must be set to "hugging_face_hub" when doing serverless inference
* `TOWER_INFERENCE_ROUTER_API_KEY` - when using ollama inference router, the API key can be left unset. When using the "hugging_face_hub" inference router, should be set to the Hugging Face token 
* `TOWER_INFERENCE_PROVIDER` - should be set to a Hugging Face Hub Inference provider like "together" or others

Curious about Inference Routers and Inference Providers? 

When using the Hugging Face Hub, it will serve as a *router* of inference requests to various inference *providers* on the platform, including "together". 

When using Ollama as the inference endpoint, "ollama" is both the router and the provider. 

To create one of these secrets, use the CLI or the Web UI:

When executing the app in local mode:

```bash
tower secrets create --environment="prod" \
  --name=TOWER_INFERENCE_ROUTER --value="hugging_face_hub"

tower secrets create --environment="prod" \
  --name=TOWER_INFERENCE_ROUTER_API_KEY --value="hf_1234567"

tower secrets create --environment="prod" \
  --name=TOWER_INFERENCE_PROVIDER --value="together"
```

## Iceberg catalogs

This example expects an Iceberg catalog with the slug `default` to be present in the environment where it is executed. 
This catalog will be used to write into a table `issue_threads` in the namespace `github`. See this [guide](https://docs.tower.dev/docs/concepts/environments#catalogs) for instructions for setting up the `default` catalog.


## Running the app

You can run the app using the Tower CLI. You don't need to specify the app name; the tower CLI will figure out what app to run based on the Towerfile.

### Running locally

When running the app locally, a local `ollama` server will serve the inference requests.

Start ollama in a separate terminal window.

```bash
ollama run deepseek-r1:14b
```

Then run the app in --local mode, use the following command. The command has some default values for the inputs (the GitHub issue) and output locations. 

```bash
tower run --local \
  --parameter=gh_repo_owner='dlt-hub' \
  --parameter=gh_repo='dlt' \
  --parameter=gh_issue_number=933 \
  --parameter=model_to_use='deepseek-r1:14b'
```

Here is what each parameter means:

- gh_repo_owner : The owner of the GitHub repo
- gh_repo : The name of the GitHub repo
- gh_issue_number : The number of the issue in that repo
- out_last_response_bucket_url : path to a folder containing the file with the summary generated by the model
- out_full_chat_bucket_url : path to a folder containing the file with the GitHub thread and the model-generated summary
- model_to_use : version of the model to use to generate the summary


### Running in "prod"

To run on Tower cloud, first make sure that you created a secret for the Hugging Face token. See "Creating app secrets" section.

Then, run the app with a slightly different set of parameters and by replacing the --local setting with the "prod" environment setting.

```bash
tower run --environment="prod" \
  --parameter=gh_repo_owner='dlt-hub' \
  --parameter=gh_repo='dlt' \
  --parameter=gh_issue_number=933 \
  --parameter=model_to_use='deepseek-ai/DeepSeek-R1' \
  --parameter=max_tokens=1000
```

A new parameter is relevant for "prod" runs: 
- max_tokens : The maximum length of output, measured in tokens


## Check the run status

You can use the following command to see how the app is progressing. Again, no
need to supply an app name as long as you're in a directory with a Towerfile.

```bash
$ tower apps show
```

You can also use the Tower [web UI](https://app.tower.dev) to learn more about the status of your app run.


## Troubleshooting

### ModuleNotFoundError error

If you get an error when executing one of the examples
```
ModuleNotFoundError: No module named 'core'
```
just add to the Python Path
```
export PYTHONPATH=.:$PYTHONPATH
```

### NotImplementedError on MPS device error

If you are trying to do local Pytorch inference on Apple Silicon and get an error when executing one of the examples
```
NotImplementedError: The operator 'aten::isin.Tensor_Tensor_out' is not currently implemented for the MPS device.
```
just run this before running the example script
```
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

