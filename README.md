# BiasedNewsGenerator

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
right model: Bild, Rt, Verschwörungsforen,  Compact (Magazin), nius
central model: Faz, Spiegel,  zeit
left model: Junge Welt, taz, Indymedia 

(scraping from different websites will be difficult) 


## UI
A simple web-based interface where a user can:

Input a topic or query for the “news”.
Receive a generated piece of “news” or scandal-laden content.

Feedback Mecanism:
Users upvote or down vote certain arcticles and posts. 


## Bigger Vision

3 Insta/ Tiktok accounts that post our news.

We pull the relevant news from tagesschau api and the generate news update from 3 perfekltives. 
The we also can get user feedback. 

### right account (Volksstimme)

### left account (Der Aufbruch)

### neutral (Klartext)
