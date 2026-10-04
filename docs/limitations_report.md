# Limitations Report

The Clinical-Impact-Aware Equipment Downtime System is a prototype and has several critical limitations that must be addressed before any consideration of real-world use:

## 1. Synthetic Data & Lack of Real Integration
The system currently uses purely synthetic data. It is not integrated with actual hospital Electronic Health Records (EHR), Computerized Maintenance Management Systems (CMMS), or scheduling systems.

## 2. Rule-Based Scoring Limitations
The algorithm uses a static, rule-based weighted sum. While this provides 100% explainability, it may fail to capture complex, non-linear interactions between clinical services that experienced hospital staff intuit naturally.

## 3. Data Quality Dependency
The system's accuracy is entirely dependent on the quality of downstream data. If a procedure is scheduled but the required equipment is not logged correctly in the IT system, the impact score will be artificially low.

## 4. Human Oversight is Mandatory
Because of potential false prioritization, human oversight is a strict requirement. The system cannot and must not autonomously dispatch technicians or cancel procedures.

## 5. Prototype Security Limitations
This prototype lacks proper authentication, authorization, and encryption protocols required for handling sensitive hospital data.

## 6. No Clinical Decision Making
This system is solely for maintenance prioritization. It does not provide clinical guidance.
