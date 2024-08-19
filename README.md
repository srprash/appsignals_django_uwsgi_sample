# appsignals_django_uwsgi_sample
Sample Django + uWsgi app running with AppSignals enabled

## Running the Django application with uWSGI
Start by creating a python virtual environment
```
python -m venv venv
source venv/bin/activate
```

Install dependencies
```
cd myproject
pip install -r requirements.txt
```

Start the application
```
export DJANGO_SETTINGS_MODULE=myproject.settings
uwsgi --ini uwsgi.ini --http 0.0.0.0:8000
```

Send traffic to application. Hitting the home address of the application will print `Hello World!`
```
curl http://127.0.0.1:8000
```

## Enbaling Application Signals

#### Install and run CloudWatch Agent 

Follow steps 1 and 2 here: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Signals-Enable-EC2.html

#### Instrument application

note: *`opentelemetry-instrument` can't be used with the `uwsgi --ini uwsgi.ini --http 0.0.0.0:8000` command. So we follow the approach of loading instrumentation via `sitecustomize.py` (similar to what is done under-the-hood for ECS or EKS platforms)*

Install ADOT Python to a custom target directory
```
pip install aws-opentelemetry-distro --target otel-auto-instrumentation-python
```

Set `sitecustomze.py` on the PYTHONPATH
```
export PYTHONPATH=<FULL_PATH_TO>/otel-auto-instrumentation-python:<FULL_PATH_TO>/otel-auto-instrumentation-python/opentelemetry/instrumentation/auto_instrumentation
```

Set the environment variables
```
export OTEL_PYTHON_DISTRO=aws_distro
export OTEL_PYTHON_CONFIGURATOR=aws_configurator
export OTEL_METRICS_EXPORTER=none
export OTEL_LOGS_EXPORTER=none
export OTEL_AWS_APPLICATION_SIGNALS_ENABLED=true
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_SAMPLER=always_on
export OTEL_AWS_APPLICATION_SIGNALS_EXPORTER_ENDPOINT=http://localhost:4316/v1/metrics
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4316/v1/traces
export OTEL_RESOURCE_ATTRIBUTES="service.name=MY_APPLICATION"
export DJANGO_SETTINGS_MODULE=myproject.settings
```

Start the application. You should see startup logs from ADOT Python.
```
uwsgi --ini uwsgi.ini --http 0.0.0.0:8000
```

**Note:** *I have observed that the above Django application when run with uWSGI produces traces but not the Application Signals metrics due to a known issue in OpenTelemetry Python related to deadlock within the parent and child processes.
The solution is to load auto-instrumentation in each uWSGI worker process separately instead of the main process. See below on how to do it for this application.*

1. Reset PYTHONPATH so that the auto-instrumentation is not loaded automatically for a process
   ```
   export PYTHONPATH=""
   ```

2. Uncomment the `aws-opentelemetry-distro` dependency in `requirements.txt` file and run `pip install -r requirements.txt` to install the ADOT Python along with other application dependencies.

3. Uncomment the lines in the `myproject/wsgi.py` file. This will import the `sitecustomize.py` and load auto-instrumentation into each worker process (configured to be 4) of uWSGI.

4. Start the application same as above `uwsgi --ini uwsgi.ini --http 0.0.0.0:8000`. You should see startup logs from ADOT Python, but repeated 4x now (for each worker process).

You should now be able to see traces and Application Signals metrics for the requests made to the `MY_APPLICATION` service.



