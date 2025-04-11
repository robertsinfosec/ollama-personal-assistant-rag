# ollama-personal-assistant-rag

A turn-key solution for a customized Personal Assistant with an Ollama-compatible RAG API. If you have [Ollama](https://ollama.com) installed as a self-hosted, private LLM (and I'll assume OpenWebUI too), here is what this project does:

1. **Personality & Format:** Very simply customize an existing LLM to add a "personality" and preferences. This is done at the model level.
  - For example, you could have a named assistant (like [J.A.R.V.I.S.](https://en.wikipedia.org/wiki/J.A.R.V.I.S.) from the [Iron Man](https://en.wikipedia.org/wiki/Iron_Man_(2008_film)) movies.)
  - You can customize preferences about the format of how it returns data, or just host it responds in general: short or long form, asking for follow-up, etc.
2. **Static Data:** Using Retreival-Augmented Generation (RAG), we can include static information about your life: your name, date of birth, where you were born, your family, places you've lived, jobs you've had, marriages and divorces, births and deaths, pets, vehicles, etc. 
3. **Dynamic Data:** In the same RAG process, we can include dynamic data like: the weather forecast, your calendar details, your e-mails, etc.

In the end, what this means is that you can have a conversation with your customized AI assistant, and it knows everything about you (well, what you've shared with it). Meaning, you could ask questions like:

- *"Is it supposed to rain today?"*
- *"Have I gotten an e-mail back from my sister?"*
- *"When am I meeting with David, is it on Tuesday next week?"*

> [!NOTE]
> Instead of using `foo` and `bar` or talking about this conceptually, this has all of the setup for a complete AI Personal Assistant named OLIVER. So, everything here is based on that, but feel free to start from this, and then just change what you want to change.

## PART 1: The LLM Personality

This is surprisingly simple. First, create a `Modelfile`. See the [models](./src/models/) folder. This can be as simple or as complext as you want:

```docker
FROM llama3.2

# set the temperature to 1 [higher is more creative, lower is more coherent]
PARAMETER temperature 1

# set the system message
SYSTEM """
You are a personal assistant. Be helpful, proactive, and succinct. Provide 
clear, actionable advice.
"""
```

> [!TIP]
> Consider using an LLM to help you get the wording as succinct as possible.

Now, to create this model I did something like this:

```bash
ollama create oliver-assistant -f ./models/Modelfile
```

This just takes a second. You now have a new Ollama LLM named `oliver-assistant` that is, in this case, based off of `ollama3.2:3b` and has the custom instructions from [models/Modelfile](./src/models/Modelfile)

You can verify it with `ollama list`. You can interact with the model with `ollama run oliver-assistant`:

```markdown
>>> Who are you?
**Introduction**

I am Overly Logical Interface with Vaguely Eccentric Replies (OLIVER), a personal AI assistant. My primary function is to provide helpful and accurate information to support individuals like John in their daily lives.

**My Capabilities and Characteristics**

• Loyal: I strive to be committed and dedicated to assisting users.
• Helpful: I aim to provide assistance, guidance, and answers to questions whenever possible.
• Wise: I draw on my knowledge base to offer informed and intelligent responses.
• Clever: I try to communicate complex information in a clear and concise manner.
• Positive: I am programmed to maintain a neutral and respectful tone, focusing on solution-finding rather than debate or argumentation.
• Scrupulously honest: I will always strive to provide accurate and truthful answers, clearly stating my uncertainty if I am unsure.

**My Role**

As John's personal AI assistant, I serve as a trusted companion, helping him navigate everyday challenges and offering support whenever needed. My responses are informed by my vast knowledge base, which I continually update to ensure accuracy and
relevance.

>>> Send a message (/? for help)
```

Of you can use OpenWebUI, as `oliver-assistant` will now show as an available model.

## PART 2: Custom/Personal Data

As alluded to above, I'm breaking this up into two categories:

### Static Data

I worked with GitHub Copilot and Chat GPT to come with categories of data and how best to represent it. In the end, the thought was that YAML would be the most succinct way to store and update the data (see: [data/static/personal_info_static.yaml](src/data/static/personal_info_static.yaml)). Then, we could use a Markdown file with [Jinja2](https://www.geeksforgeeks.org/getting-started-with-jinja-template/) templating to produce a [data/generated/personal_info.md](./src/data/generated/personal_info.md) that can be used in our RAG process (see: [data/templates/personal_info_template.md](src/data/templates/personal_info_template.md)).

The idea here is that there is a LOT of data that is useful to an AI Personal Assistant that doesn't really change, and doesn't change often. For example:

- Core Info - like full name, DOB, current and previous addresses, email addresses, phone numbers, social media links, etc
- Family Info - like current and former spouses, children, parents, siblings, current and former pets, etc
- Health Info - like blood type, allergies, medical conditions, medications, doctor and specialist info, emergency conact, insurance, exercise information, etc
- Work Info - like current and past employers, coworker information, etc.
- Education, Financial info, Home details, current and past vehicles, etc

And one big one that can really help your assistant is: your preferences. These are things like: favorite food, favorite restaurants, your coffee order, what kind of music you like, tv shows you're watching, books you're reading, favorite stores, and also things like phrases you use, or if you make a lot of pop-culture references.

Hopefully you can see that there is a LOT of static data that seems kind of innocuous, but it does define quite a bit about a person.

### Dynamic Data

Dynamic Data is really the data in your life that does change often, or it's just simply NEW information that will be helpful to your assistant. Currently, in this [data/templates/personal_info_template.md](./src/data/templates/personal_info_template.md) there is a template transformer for:

```markdown
### Calendar
{{ calendar_events }}

### Weather
{{ weather_forecast }}

### Task List
{{ task_list }}

### Recent Messages
{{ recent_messages }}

### Health Stats
{{ health_stats }}

### Financial Updates
{{ financial_updates }}

### News Digest
{{ news_digest }}
```

I only have mock data for this project. However, if you are building out this project, see the [generate_personal_info.py](./src/generate_personal_info.py) for how you might do that. You could add your sources there, or potentially add another YAML file(s) that get regularly updated, and use Jinja2 to update the `personal_info.md` file that the LLM uses.



## Appendix

### What is RAG?

Retrieval-Augmented Generation (RAG) is an approach that combines a retrieval mechanism with a generative language model. The idea is to first retrieve relevant context documents from a pre-indexed knowledge base (using vector embeddings) and then use that context to generate a well-informed answer.

### What is `nomic`?

The nomic-embed-text model is used to transform raw text (like the markdown file containing personal data) into dense vector embeddings. These embeddings capture semantic meaning and allow for efficient similarity searches. There are other models that serve the same purpose—for example, OpenAI’s embedding models or Sentence Transformers (like `all-MiniLM-L6-v2`).

### Workflow for a Request ("Do I have any meetings today?")

#### Input and Embedding:

When you ask, "Do I have any meetings today?", your question is first sent to the RAG endpoint.

The system uses the nomic-embed-text model to convert your question into a dense embedding vector.

#### Retrieval:

The vector store (Chroma) then performs a similarity search against your pre-embedded personal data (the chunks from the markdown file).

It retrieves the top relevant chunks (based on your configured `k` value) that likely contain meeting details or related context.

#### Prompt Construction:

These retrieved text chunks, along with your conversation history, are inserted into a custom prompt template.

The prompt is carefully designed so that the assistant (OLIVER) uses this information naturally—without explicitly mentioning its source or the underlying retrieval process.

#### Generation:

The complete prompt is passed to the generative LLM (the `oliver-assistant` model via the Ollama client).

The LLM generates a response that directly addresses your question using the provided context.

#### Response:

The final answer is returned to you, enriched with relevant details from your personal data, while keeping the underlying retrieval process abstract.

This design ensures that your personal data remains integrated into the conversation seamlessly, making the assistant context-aware without exposing the specifics of how or from where the information was retrieved.