from django.core.exceptions import ObjectDoesNotExist

from backend.models import Workflow
def get_workflow_tool(workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    nodes = workflow.nodes
    description = workflow.description
    start = nodes[0]
    parameters = []
    for input in start["inputs"]:
        parameters.append(input["type"])
    return {
            "type":"workflow",
            "function":{
                "name": workflow.name,
                "description": description,
                "parameters":parameters
            }
            }

