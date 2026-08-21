# SAMPLE 

TODOs Aug 20th
	• In the `updated-prompts` branch test the prompt updates
	• First, update the QA sheet after removing the 74 problematic queries from them
		○ Use the QA retest direct queries skill (on the modified and cleaned up QA Sheet)
			§ Test gpt 5.4 mini on that data with OG System Prompt
			§ Test gpt 5.4 mini on the new System Prompt
	• Improve system prompts by somehow "visualizing it"
	• Do RCA Parallely for Multi-Turn Conversations
	• Integrate the New Taxonomy:
		○ Take old static excel sheet (Shared with AV)
			§ This will contain the reference to the old taxonomy, descriptions, ids, names etc
		○ Take new excel sheet (Shared by AV)
			§ This will contain the updated Taxonomy, updated descriptions, ids, names etc
			§ This sheet's description will be our source of truth and disambiguations as well.
				□ For now, we will be using them as is.
				□ Later we can incorporate more disambiguation rules (on a need to based, post evals check)
				□ We will make sure to store the legacy intent descriptions and disambiguation rules (as well as entity descriptions etc) as well, so that we can refer to these in case of any regressions
			§ The changes should be highlighted as well
			§ Some columns here are useless/wrong, we will have to review those separately
		○ Make sure to mark our changes made by us (in description/widget id etc) a different font (say purple), so that it will be easier for me to review. Color coding is important.
		○ Take the Intent changes Markdown Doc(")
		○ Strategically Update:
			§ Check entity widget/redirection/fsm naming logic/scheme
				□ This will also update these column values:
				Entity name	Deeplink	widget id	fsm id
			§ Create the simple update strategy manually. First get an implementation Plan for this task.
			§ Migrate the easy changes one by one.
			§ Try using the cut and paste philosophy as much as applicable.
			
	• IDEAS TO TRY for Enhancement:
		○ Add examples more aggressively. (Examples are low in token volume)
		○ Examples let MID know better, what the scope of each Intent is, much much better
(This is because IFB seems to be behaving nicely)
