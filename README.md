
# BiasedNewsGenerator

## Overview
This project was developed as part of the voluntary course "Machine Learning and AI." We built a pipeline that fetches news from the Tagesschau API and selects a topic, which is then processed by our custom fine-tuned LLM model.

Our fine-tuned model has been trained on several hundred articles collected from far-right media sources. After preprocessing these articles and generating a Q&A dataset (TBD: whether reasoning should also be generated), we fine-tuned the model to improve its ability to rewrite these articles while incorporating their inherent bias.

## Model:
finetune model
multiple Models with different Opinions: right, left, conspiracy -> Budget Constraints?

### one model scenario:
Q&A with both left, neutral and right questions. Slider impacts prompt

### 3 model scenarion:
One right, left and neutral model trained with data

huggingface basemodel without constraints
## Backend:

Feedback from User for further training.

### Webscraping from
right model: Bild, Rt, Verschwörungsforen,  Compact (Magazin), nius, Epoch Times
central model: Faz, Spiegel,  zeit, Tageschau
left model: Junge Welt, taz, Indymedia, Epoch Times 

(scraping from different websites will be difficult) 


## UI
A simple web-based interface where a user can:

Input a topic or query for the “news”.
Receive a generated piece of “news” or scandal-laden content.

### Feedback:
Most important feedback will be the interaction and reaction it creates.
To then nudge the Model to generate similar content

#### Internal UI
Users upvote or down vote certain arcticles and posts. 

#### External 
Depending on views and likes from Insta/TikTok.



## Bigger Vision

3 Insta/ Tiktok accounts that post our news.

We pull the relevant news from tagesschau api and the generate news update from 3 perfekltives. 
The we also can get user feedback. 

### right account (Volksstimme)
Ein Volk, Eine Wahrhiet, Eine Zeitung

### left account (Der Aufbruch)
Für ein neues Zeitalter der Gerechtigkeit

### neutral (Klartext)
Der unabhängige Blick

### government-aligned (Der Kritische Beobachter)
Für unabhängigen Journalismus 
