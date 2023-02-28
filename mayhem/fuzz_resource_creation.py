#! /usr/bin/env python3
import atheris
import json
import random
import sys

import fuzz_helpers

with atheris.instrument_imports(include=['fhir.resources']):
    from fhir.resources.fhirtypesvalidators import MODEL_CLASSES
    from fhir.resources.patient import Patient
    from fhir.resources.organization import Organization
    from fhir.resources import construct_fhir_element
    from pydantic.error_wrappers import ValidationError

available_class_names = list(MODEL_CLASSES.keys())

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    test = fdp.ConsumeIntInRange(0, 2)

    try:
        if test == 0:
            Organization.parse_raw(fdp.ConsumeRemainingBytes())
        elif test == 1:
            Patient.parse_raw(fdp.ConsumeRemainingBytes())
        elif test == 2:
            json_obj = json.loads(fdp.ConsumeRemainingString())
            construct_fhir_element(fdp.PickValueInList(available_class_names), json_obj)
    except (ValidationError, json.JSONDecodeError):
        return -1
    except LookupError as e:
        if random.random() > 0.9:
            raise e
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
