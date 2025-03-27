
# BiasedNewsGenerator

## Overview
This project was developed as part of the voluntary course "Machine Learning and AI." We built a pipeline that fetches news from the Tagesschau API and selects a topic, which is then processed by our custom fine-tuned LLM model.

Our fine-tuned model has been trained on several hundred articles collected from far-right media sources. After preprocessing these articles and generating a Q&A dataset (TBD: whether reasoning should also be generated), we fine-tuned the model to improve its ability to rewrite these articles while incorporating their inherent bias.

## Scraping

[WebscraperNius](https://github.com/paulKlarer/BiasedNewsGenerator/tree/main/WebscraperNius)

## QA-Sheet generation

[QASheetCreation](https://github.com/paulKlarer/BiasedNewsGenerator/tree/main/QASheetCreation)

## Finetuning

## Evaluation

[evaluation](https://github.com/paulKlarer/BiasedNewsGenerator/tree/main/evaluation)

## Backend & Frontend

[website](https://github.com/paulKlarer/BiasedNewsGenerator/tree/main/website)
