Configure your processes
------------------------

1. Access the `Automation` menu.
2. Create a new Automation Configuration.
3. Set the model and domains.
4. Go to Configuration -> Filters to create filters as a preconfigured domains.
  Filters can be established in the proper field in the Automation Configuration record.
5. Create the different steps by clicking the "ADD" button inside the automation configuration form.
6. Create child steps by clicking the "Add child activity" at the bottom of a created step.
7.
8. Select the kind of configuration you create. You can choose between:
    * *Periodic configurations*: every 6 hours, a process will check if new records need to be created.
    * *On demand configurations*: user need to execute manually the job.
9. Press `Start`.
10. Inside the process, you can check all the created items.

![Configuration Screenshot](./static/description/configuration.png)

Configuration of steps
---------------------------

Steps can trigger one of the following options:

- `Mail`: Sends an email using a template.
- `Server Action`: Executes a server action.
- `Activity`: Creates an activity to the related record.

All the steps need to specify the moment of execution. We will set the number of hours/days and a trigger type:

- `Start of workflow`: It will be executed at the previously-configured time after we create the record.
- `Execution of another step`: It will be executed at the previously-configured time after the previous step is finished properly.
- `Mail opened`: It will be executed at the previously-configured time after the mail from the previous step is opened.
- `Mail not opened`: It will be executed at the previously-configured time after the mail from the previous step is sent if it is not opened before this time.
- `Mail replied`: It will be executed at the previously-configured time after the mail from the previous step is replied.
- `Mail not replied`: It will be executed at the previously-configured time after the mail from the previous step is opened if it has not been replied.
- `Mail clicked`: It will be executed at the previously-configured time after the links of the mail from the previous step are clicked.
- `Mail not clicked`: It will be executed at the previously-configured time after the mail from the previous step is opened and no links are clicked.
- `Mail bounced`: It will be executed at the previously-configured time after the mail from the previous step is bounced back for any reason.
- `Activity has been finished`: It will be executed at the previously-configured time after the activity from the previous action is done.
- `Activity has not been finished`: It will be executed at the previously-configured time after the previous action is executed if the related activity is not done.

Important to remember to define a proper template when sending the email.
It will the template without using a notification template.
Also, it is important to define correctly the text partner or email to field on the template

Records creation
----------------

Records are created using a cron action. This action is executed every 6 hours by default.

Step execution
------------------

Steps are executed using a cron action. This action is executed every hour by default.
On the record view, you can execute manually an action.
