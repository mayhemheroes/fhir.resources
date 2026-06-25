#! /usr/bin/env python3
import atheris
import json
import random
import sys

import fuzz_helpers

with atheris.instrument_imports(include=['fhir.resources', 'fhir_core']):
    from fhir.resources import get_fhir_model_class
    from fhir.resources.patient import Patient
    from fhir.resources.organization import Organization
    from pydantic import ValidationError

# Representative FHIR R5 resource types exercised by the generic-parse path. A curated list keeps
# harness startup fast (importing all ~200 models would stall the fuzzer's first iterations).
available_class_names = [
    'Patient', 'Organization', 'Observation', 'Condition', 'Encounter', 'Procedure',
    'MedicationRequest', 'Bundle', 'Practitioner', 'AllergyIntolerance', 'DiagnosticReport',
    'Immunization', 'CarePlan', 'Goal', 'Device', 'Location', 'Medication',
    'DocumentReference', 'Coverage', 'Claim', 'ServiceRequest', 'Specimen', 'RelatedPerson',
    'Appointment', 'CodeableConcept', 'Quantity', 'HumanName', 'Address', 'ContactPoint',
]


def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    test = fdp.ConsumeIntInRange(0, 2)

    try:
        if test == 0:
            Organization.model_validate_json(fdp.ConsumeRemainingBytes())
        elif test == 1:
            Patient.model_validate_json(fdp.ConsumeRemainingBytes())
        elif test == 2:
            json_obj = json.loads(fdp.ConsumeRemainingString())
            klass = get_fhir_model_class(fdp.PickValueInList(available_class_names))
            klass.model_validate(json_obj)
    except (ValidationError, json.JSONDecodeError, ValueError, TypeError, KeyError, AttributeError):
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
