In standard Odoo, when creating a new record through Server Actions, the framework often relies on **`name_create(self.value)`**, which only fills in the **`name`** field.
This is limiting in scenarios where multiple fields need to be pre-populated or dynamically computed.
