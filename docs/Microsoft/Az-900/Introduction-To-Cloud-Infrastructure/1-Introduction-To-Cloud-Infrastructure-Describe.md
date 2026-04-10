
## What is cloud computing?

Cloud computing is the use of computing hardware located in a data center over the internet.

Cloud providers offer their different services, but the main services everyone can provide includes compute power and storage.

Compute power is the amount of processing power your computer can do. Rather than being limited by your hardware at home, in the cloud you can easily choose more powerful hardware as you need it.

Storage is how much data you can store on your computer. Rather than running out of storage on your own computer, the cloud lets you expand how much storage you have as you need it.

The main benefits of cloud computing is that you don't have to maintain the hardware, software and operating system, you only pay for the compute power and storage you need, and the cloud enables rapid change of IT infrastructure as your use case needs it.

## Describe the shared responsibility model

The shared responsibility model outlines the various responsibilities associated with using a data centre, with some of these responsibilities falling on the cloud provider, while others are handled by the customer.

There are various stages of this model, ranging from on premises where the customer owns every responsibility, to Software as a Service (SaaS) where the cloud provider handles almost everything.

Shared Responsibility model table:

![Diagram showing the responsibilities of the shared responsibility model.](../../../../resources/shared-responsibility-b3829bfe.svg)

You will always be responsible for: Information and data stored in the cloud, Devices allowed to connect to your cloud services, The accounts and identities of people, services and devices within your organisation

The cloud provider will always be responsible for: the physical data centre, the physical network, the physical hosts (computers)

Depending on the model chosen, you may be responsible for: Operating systems, Network controls, Applications, Identity and infrastructure

## Define cloud models

Private cloud: Cloud services provided to one organisation only. The data centre utilised can be owned by the same company or provided by a third party but regardless of how it is provided the entire data centre id dedicated to only one organisation.

Public cloud: Cloud services and the associated data centres are owned by a third party, and anyone from the public can purchase to use the cloud services. The data centres and cloud services are used by multiple clients at once, making it a publicly available service unlike the private cloud model.

Hybrid cloud: The combines the private and public cloud models, where some cloud capabilities are controlled by the organisation themselves while other cloud services are provided by a third party. It combines the privacy of private cloud and the flexibility of public cloud in one model.

Common attributes of the main cloud models:

| **Public cloud** | **Private cloud** | **Hybrid cloud** |
| --- | --- | --- |
| No capital expenditures to scale up | Organizations have complete control over resources and security | Provides the most flexibility |
| Applications can be quickly provisioned and deprovisioned | Data is not collocated with other organizations’ data | Organizations determine where to run their applications |
| Organizations pay only for what they use | Hardware must be purchased for startup and maintenance | Organizations control security, compliance, or legal requirements |
| Organizations don’t have complete control over resources and security | Organizations are responsible for hardware maintenance and updates |     |

Multi cloud: A modern cloud model which utilises multiple public third party cloud providers. Cutting edge features, efficient costs for niche use cases or being mid migration to a new cloud provider are the main reasons this model is used today.

Azure Arc: This is a suite of technologies used by Azure to help you manage your cloud setup, and can handle any of the above mentioned models.

Azure VMware Solution: VMware is typically used in private cloud environments to host virtual machines running services, applications and databases. Azure VMware Solution helps you run your private VMware virtual machines as you migrate to a public or hybrid cloud model.

## Describe the consumption-based model

Capital expenditure (CapEx): One time purchase of resources, such as building a data centre.

Operational expenditure (OpEx): Spending money on services over time, such as cloud services.

Cloud computing is a consumption based model, where there is no payment for the physical hardware (like building a data centre) and instead you only pay for the hardware you use (if you use one CPU, you pay for one CPU rather than buying all 10 CPUs and only using one of them).

Traditional CapEx pricing, such as building a data centre, require you to predict how much CapEx to invest. If you over estimate, you buy too much hardware. If you under estimate you don't have enough hardware.

Consumption based models have benefits including no upfront costs, no costly maintenance, you can pay only for what you use, stop paying anytime.

Cloud computing uses Pay-As-You-Go (PAYG) pricing model.

## Describe the benefits of high availability and scalability in the cloud

&nbsp;