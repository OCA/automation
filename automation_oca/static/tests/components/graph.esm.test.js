import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class GraphTest extends models.Model {
    _name = "graph.test";
    data = fields.Generic({type: "new field type without widget"});
    /*
        We cannot use json, because odoo is passing JSON as strings on the test
        but it is an object in real life :(
    */

    _records = [
        {
            id: 1,
            data: {
                done: [
                    {x: 1, y: 2, name: "DONE"},
                    {x: 2, y: 2, name: "DONE"},
                ],
                error: [
                    {x: 1, y: 3, name: "DONE"},
                    {x: 2, y: 1, name: "DONE"},
                ],
            },
        },
    ];
}

defineModels([GraphTest]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check Automation Graph Widget", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "graph.test",
        arch: `
            <form>
                <field name="data" widget="automation_graph" />
            </form>`,
    });
    expect(`[name="data"]`).toHaveCount(1);
    expect(`[name="data"] canvas`).not.toBeEmpty();
});
