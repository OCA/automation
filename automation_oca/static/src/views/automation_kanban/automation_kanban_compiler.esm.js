/** @odoo-module */

import {KanbanCompiler} from "@web/views/kanban/kanban_compiler";

export class AutomationKanbanCompiler extends KanbanCompiler {
    setup() {
        super.setup();
        this.compilers.push({
            selector: ".o_automation_kanban_child_add_button[t-att-trigger-type]",
            fn: this.compileHierarchyAddButton,
        });
    }
    compileHierarchyAddButton(el) {
        el.setAttribute(
            "t-on-click",
            "() => this.addNewChild({trigger_type: " +
                el.getAttribute("t-att-trigger-type") +
                "})"
        );
        return el;
    }
}
