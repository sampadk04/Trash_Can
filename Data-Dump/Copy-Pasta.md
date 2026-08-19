# SAMPLE 

Okay, so I was talking about the **MID**, which is one of the most important parts of our system. Every time a query comes in, it generally hits the MID for some form of intent detection, unless it is already part of an existing journey or an existing IFB flow. So, for most queries, the MID is going to be involved.

I was looking at the **system prompt and user prompt—essentially everything the LLM sees—and they currently feel somewhat unstructured**.

Over time, in order to improve the performance of the LLM and make it behave the way we want, we have added a sufficient number of examples, instructions, signals, keywords, and nuances into the prompts. As a result, however, the prompts have become quite bloated.

What I want to explore is whether we can **retain all of the useful information that is currently present, carefully dissect it into its constituent parts, and restructure it into a much cleaner and more organized form**. The goal is to create something that the LLM can interpret more reliably, without fundamentally changing the information that it receives.

Currently, there may be a lot of examples, keywords, rules, and other signals scattered throughout the system prompt. Some of these may simply be mentioned here and there without receiving sufficient emphasis. As a result, certain signals that are actually extremely important may not stand out strongly enough to the model.

For the **MID**, for example, two of the most important signals are:

* the **intent description**, and
* the **disambiguation rules**.

These should ideally be clearly isolated, structured, and emphasized so that the MID can reason over them properly.

The same idea applies to the **IFB**.

For an IFB, the **entity-level information** becomes extremely important because it helps establish the scope of a particular intent. The model needs to clearly understand things such as the entity descriptions, the possible entity values, and how those entities define what kinds of queries fall within the scope of that IFB.

One specific problem we noticed within the **IFB switcher block** is that, in some cases, the user's query is actually clearly within the scope of a particular entity based on the entity description, the possible entity values, and the surrounding context that we are already providing to the model.

The signal can admittedly be quite subtle. However, even if it is subtle, the expectation is that the switcher should still have been able to pick it up from the entity description, entity values, and whatever other relevant context we are already providing. Instead, in some cases, it incorrectly decides that the user has switched to another intent even though the query should still fall within the scope of the existing IFB.

This is therefore one of the behaviors that I specifically want to examine once we start restructuring the prompts properly.

The important constraint here is that **we do not initially want to change the underlying information content of the prompt**.

We are not trying to solve the problem by adding more examples, removing instructions, rewriting the business logic, or giving the model additional signals. The amount and nature of information available to the model should remain essentially constant. We should be retaining the same core information, instructions, keywords, examples, descriptions, disambiguation rules, entity information, and other relevant signals.

In other words, **the amount of information that we are gaining or losing should ideally remain the same**. Similarly, the instructions that the model receives should remain the same in substance.

What we want to change is primarily the **structure and presentation of that information**.

For example, we could experiment with:

* grouping related instructions together,
* clearly separating intent descriptions from disambiguation rules,
* isolating entity descriptions and entity values,
* moving examples closer to the rules or concepts that they illustrate,
* introducing clearer sections and hierarchy,
* using XML tags or similar delimiters,
* emphasizing important keywords and decision signals using markdown bolds,
* separating contextual information from actual decision rules,
* and generally moving existing pieces of information around so that the prompt is easier for the model to parse.

The idea is essentially to make the prompt **cleaner, more structured, and easier to visually and semantically navigate**, while keeping the underlying content as close to identical as possible.

So, at least initially, this becomes a controlled experiment.

We keep the **keywords, examples, rules, descriptions, instructions, entity information, and overall amount of information essentially the same**, and we change primarily how that information is organized and represented.

Then we can evaluate whether these relatively simple prompt-engineering changes—better sectioning, hierarchy, XML tags, delimiters, placement of examples, grouping of related information, and similar techniques—actually improve the reasoning behavior of the MID, IFB, and switcher.

The IFB switcher issue is particularly useful as a concrete test case. If the existing entity description and entity values already contain enough information to establish that a subtle query remains within the scope of the current entity, then we want to see whether **making those signals structurally clearer and more prominent causes the model to recognize them more consistently**.

More broadly, the goal is to understand how much performance we can gain purely from **better prompt organization**, without changing the actual knowledge or instructions supplied to the model.

If behavior improves while the underlying information remains constant, then we have a much stronger indication that the improvement is coming from the way the information is structured and surfaced to the LLM, rather than simply because we gave the model more information.
