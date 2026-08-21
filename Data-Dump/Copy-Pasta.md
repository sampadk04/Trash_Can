# SAMPLE 

TODOs

* Clean up OpenAI client handling

  * Simplify production client/payload structure
  * Create clear client entry points per block
  * Align production and testing client configuration
  * Streamline multi-LLM testing setup

* Unify the taxonomy

  * Merge the legacy taxonomy with the new PM-provided taxonomy
  * Use the new taxonomy as the source of truth
  * Preserve legacy descriptions/rules for regression reference
  * Review and clean up incorrect/unnecessary columns
  * Highlight our changes clearly for PM review
  * Incorporate the Intent Changes Markdown doc

* Update taxonomy mappings

  * Review entity/widget/redirection/FSM naming
  * Update related fields (entity name, deeplink, widget ID, FSM ID)
  * Create a simple migration plan
  * Migrate straightforward changes first

* Restructure and optimise the IFB prompt

  * Clean up system + user prompt structure
  * Make examples and taxonomy sections easy to maintain
  * Extract examples for PM review
  * Test updated prompts on the existing dataset
  * Start with MID blocks and self-hosted Gemma
  * Expand testing to other blocks as needed

* Improve examples

  * Add more representative examples
  * Use examples to better define intent scope
  * Validate impact through evaluation

* RCA / validation

  * Validate client and payload behaviour
  * Check for taxonomy/prompt regressions
  * Run RCA for multi-turn conversations in parallel
