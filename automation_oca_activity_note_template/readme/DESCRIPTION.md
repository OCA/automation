This module extends the **Activity** step type in `automation_oca` with the ability
to select a **mail template** as the source for the activity's summary and note.

When a mail template is selected on an automation step:

- The template **subject** is rendered and used as the **activity summary**.
- The template **body** is rendered and used as the **activity note**.

Both fields are rendered using the `inline_template` engine, which supports
`{{ object.field }}` and `{{ object.method() }}` expressions evaluated against
the target record at the moment the activity is created.

This makes it straightforward to generate **dynamic, personalised activity notes**
by calling a method on the target model from inside the template body.
