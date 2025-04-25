from odoo.tools.sql import SQL


def add_complex_left_join(
    query,
    lhs_alias,
    lhs_column,
    rhs_table,
    rhs_column,
    link,
    extra_conditions,
    params,
):
    """
    Adds a LEFT JOIN with additional conditions to the query.
    Args:
        query: Odoo Query object
        lhs_alias: Left table alias
        lhs_column: Left table column for the join condition
        rhs_table: Right table name
        rhs_column: Right table column for the join condition
        link: Suffix to generate the right table alias
        extra_conditions: Additional conditions for the JOIN
        params: Parameters for the additional conditions
    Returns:
        str: The generated alias for the right table
    """
    # Generate the alias for the right table
    rhs_alias = query.make_alias(lhs_alias, link)

    # Build the base JOIN condition
    base_condition = f'"{lhs_alias}"."{lhs_column}" = "{rhs_alias}"."{rhs_column}"'

    # If there are additional conditions, format and add them
    if extra_conditions:
        # Replace {rhs} with the actual alias
        formatted_conditions = extra_conditions.format(rhs=rhs_alias)
        full_condition = f"{base_condition} AND {formatted_conditions}"
    else:
        full_condition = base_condition

    # Add the JOIN to the query
    query.add_join("LEFT JOIN", rhs_alias, rhs_table, SQL(full_condition, *params))

    return rhs_alias
