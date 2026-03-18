Configure a mail template
--------------------------

1. Go to **Email** → **Templates** and create a new template.
2. Set the **Applies To** model to match the model used in your automation
   (e.g. *Contact*, *CRM Lead*).
3. Write the **Subject** — it will become the **activity summary**.
   Use `{{ object.field }}` expressions to include record-specific data.
4. Write the **Body** — it will become the **activity note**.
   You may call methods on `object`, for example:

   ```
   {{ object.generate_note() }}
   ```

Configure the automation step
------------------------------

1. Open an **Automation Configuration** and add or edit an **Activity** step.
2. In the **Activity** tab, select the template in the **Note Template** field.
3. The static **Summary** and **Note** fields are hidden when a template is selected,
   as they are replaced by the rendered template output.
4. Save and start the automation as usual.

When the step runs, the template subject and body are rendered individually for
each target record and set as the activity summary and note respectively.
