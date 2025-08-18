Instead of using the basic **`name_create(self.value)`**, which only sets the **`name`** field, this module allows you to:

- Configure multiple field/value pairs (**`field_default_value_ids`**) for the record to be created.
- Use dynamic Python expressions to compute values at runtime.


## Configuration

1. Navigate to:
   **Settings → Technical → Actions → Server Actions**

2. Create a new action with type **"Create Record"**.

3. In the **Field Default Values** section, you can define default values for fields by selecting a field and assigning a value.
   The value can be:
   - A static string
   - A Python expression to compute values dynamically based on the source record

### Available Variables and Helpers
- **`object`**: the source record
  *(e.g., `object.name`, `object.user_id.id`)*
- **`context_today()`**: current date
  *(e.g., `context_today()`)*
- **`relativedelta`**: to shift dates
  *(e.g., `context_today() + relativedelta(days=10)`)*

⚠️ **Note for Many2one fields:**
Make sure to return the **ID** of the record.
Example:
```python
object.user_id.id
```

### Examples
1. Set name from the source record:
```python
'Lead for ' + object.name
```

2. Set today's date:
```python
context_today()
```

3. Set a future date (10 days from today):
```python
context_today() + relativedelta(days=10)
```

4. Assign current user:
```python
object.user_id.id
```
