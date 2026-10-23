# Claims Intelligence

This context describes how claim information is converted into non-decisional signals that help an insurance operations team prioritize human review.

## Language

**Claims Reviewer**:
An internal insurance operations user who examines claim information and recommendations to prioritize human review.
_Avoid_: Customer, policyholder, applicant

**Claim Queue**:
The searchable collection of claims available to a claims reviewer, showing review priority, estimated cost, and last update.
_Avoid_: Customer list, model queue

**Motor Claim**:
A request under an existing personal motor-insurance policy to respond to loss or damage arising from an incident.
_Avoid_: Application, prospect, potential customer

**Final Paid Amount**:
The total synthetic claim payment known after a motor claim is closed. It is a training label only when the claim has matured sufficiently to be treated as complete.
_Avoid_: Initial estimate, current payment, review priority

**Claim Severity**:
The eventual total amount paid for a claim, estimated before that amount is fully known.
_Avoid_: Review priority, urgency, risk score

**Review Priority**:
The urgency with which a claim should receive human review, expressed as `standard`, `elevated`, or `urgent`. It does not determine coverage, claim validity, fraud, or payment.
_Avoid_: Claim severity, risk level, decision

**Recommended Review Priority**:
The review priority suggested by the system from the available claim information and severity prediction.
_Avoid_: Reviewer judgment, final decision

**Reviewer-Selected Priority**:
The review priority recorded by a claims reviewer together with a reason. It is distinct from the system's recommendation and from the claim's final paid amount.
_Avoid_: Model label, recommended review priority, coverage decision

**Severity Prediction**:
An estimate of a claim's eventual total paid amount produced from information available at prediction time.
_Avoid_: Review decision, coverage decision, predicted information

**Prediction History**:
The ordered record of a claim's severity predictions, including the information known at each prediction moment. Earlier predictions remain available when new information leads to an updated prediction.
_Avoid_: Latest score, overwritten prediction
