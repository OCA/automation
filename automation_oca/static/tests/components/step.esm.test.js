import {click, queryAllTexts} from "@odoo/hoot-dom";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {animationFrame} from "@odoo/hoot-mock";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class Configuration extends models.Model {
    step_ids = fields.One2many({
        relation: "configuration.step",
        relation_field: "configuration_id",
    });
    _records = [
        {
            id: 1,
            step_ids: [1, 2, 3],
        },
        {
            id: 2,
            step_ids: [4],
        },
    ];
}

class ConfigurationStep extends models.Model {
    _name = "configuration.step";
    configuration_id = fields.Many2one({relation: "configuration"});
    parent_id = fields.Many2one({relation: "configuration.step"});
    name = fields.Char();
    _records = [
        {
            id: 1,
            configuration_id: 1,
            name: "Step 1",
        },
        {
            id: 2,
            configuration_id: 1,
            name: "Step 2",
        },
        {
            id: 3,
            configuration_id: 1,
            name: "Step 3",
            parent_id: 1,
        },
        {
            id: 4,
            configuration_id: 2,
            name: "Step 4",
        },
    ];
}
defineModels([Configuration, ConfigurationStep]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check Activity Sort", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1, 2],
        resModel: "configuration",
        arch: `
            <form>
                <field name="step_ids" widget="automation_step" mode="kanban" >
                    <kanban>
                        <templates>
                            <t t-name="card">
                                <field name="name"/>
                                <field name="parent_id" />
                                <field class="o_field_id" name="id" />
                            </t>
                        </templates>
                    </kanban>
                </field>
            </form>`,
    });
    expect(`[name="step_ids"]`).toHaveCount(1);

    expect(`[name="step_ids"] .o_kanban_record:not(.o_kanban_ghost)`).toHaveCount(3);
    expect(
        queryAllTexts(
            `[name="step_ids"] .o_kanban_record:not(.o_kanban_ghost) .o_field_id`
        )
    ).toEqual(["1", "3", "2"]);
});

test("Check Activity Click Record ", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1, 2],
        resModel: "configuration",
        arch: `
            <form>
                <field name="step_ids" widget="automation_step" mode="kanban" >
                    <kanban>
                        <templates>
                            <t t-name="card">
                                <field name="name"/>
                                <field name="parent_id" />
                                <field class="o_field_id" name="id" />
                            </t>
                        </templates>
                    </kanban>
                    <form class="o_step_form">
                        <field class="field_name" name="name"/>
                    </form>
                </field>
            </form>`,
    });
    expect(`[name="step_ids"]`).toHaveCount(1);
    expect(".o_step_form").toHaveCount(0);
    await click(`[name="step_ids"] .o_kanban_record:not(.o_kanban_ghost)`);
    await animationFrame();
    expect(".o_step_form").toHaveCount(1);
    expect(".o_step_form [name='name'] input").toHaveValue("Step 1");
});

test("Check Activity Click Button", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1, 2],
        resModel: "configuration",
        arch: `
            <form>
                <field name="step_ids" widget="automation_step" mode="kanban" >
                    <kanban>
                        <templates>
                            <t t-name="card">
                                <field name="name"/>
                                <field name="parent_id" />
                                <field class="o_field_id" name="id" />
                                <div
                                    t-att-trigger-type="1"
                                    class="o_automation_kanban_child_add_button"
                                >Add Child</div>
                            </t>
                        </templates>
                    </kanban>
                    <form class="o_step_form">
                        <field name="name"/>
                    </form>
                </field>
            </form>`,
    });
    expect(`[name="step_ids"]`).toHaveCount(1);
    expect(".o_step_form").toHaveCount(0);
    await click(
        `[name="step_ids"] .o_kanban_record:not(.o_kanban_ghost) .o_automation_kanban_child_add_button`
    );
    await animationFrame();
    expect(".o_step_form").toHaveCount(1);
    expect(".o_step_form [name='name'] input").toHaveValue("");
});
