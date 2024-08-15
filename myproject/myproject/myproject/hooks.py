import uwsgidecorators
import logging

logger = logging.getLogger('django')

@uwsgidecorators.postfork
def post_fork_function():
    try:
        logger.warning('INSIDE HOOKS.PY:: attempting to load auto-instrumentation')
        from opentelemetry.instrumentation.auto_instrumentation import sitecustomize
    except ImportError:
        logger.warning('auto-instrumentation not available')
        pass

