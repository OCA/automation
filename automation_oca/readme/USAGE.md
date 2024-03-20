Configure your processes
------------------------

1. Access the `Automation` menu.
2. Create a new Configuration.
3. Set the model and filters.
4. Create the different activities.
5. Press `Start`. Now, every 6 hours, a process will check if new records need to be created.
6. Inside the process, you can check all the created items.

![Configuration Screenshot](./static/description/configuration.png)

Configuration of activities
---------------------------

Activities can trigger one of the following options:

- `Email`: Sends an email using a template.
- `Server Action`: Executes a server action.
- `Activity`: Creates an activity to the related record.

All the activities need to specify the moment of execution. We will set the number of hours/days and a trigger type:

- `Start of workflow`: It will be executed at the previously-configured time after we create the record.
- `Execution of another activity`: It will be executed at the previously-configured time after the previous activity is finished properly.
- `Mail opened`: It will be executed at the previously-configured time after the mail from the previous activity is opened.
- `Mail not opened`: It will be executed at the previously-configured time after the mail from the previous activity is sent if it is not opened before this time.
- `Mail replied`: It will be executed at the previously-configured time after the mail from the previous activity is replied.
- `Mail not replied`: It will be executed at the previously-configured time after the mail from the previous activity is opened if it has not been replied.
- `Mail clicked`: It will be executed at the previously-configured time after the links of the mail from the previous activity are clicked.
- `Mail not clicked`: It will be executed at the previously-configured time after the mail from the previous activity is opened and no links are clicked.
- `Mail bounced`: It will be executed at the previously-configured time after the mail from the previous activity is bounced back for any reason.
- `Activity done`: It will be executed at the previously-configured time after the activity from the previous action is done.
- `Activity not done`: It will be executed at the previously-configured time after the previous action is executed if the related activity is not done.

Important to remember to define a proper template when sending the email.
It will the template without using a notification template.
Also, it is important to define correctly the text partner or email to field on the template

Records creation
----------------

Records are created using a cron action. This action is executed every 6 hours by default.

Activity execution
------------------

Activities are executed using a cron action. This action is executed every hour by default.
On the record view, you can execute manually an action.
