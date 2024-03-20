/** @odoo-module */

import {AutomationKanbanCompiler} from "./automation_kanban_compiler.esm";
import {KanbanRecord} from "@web/views/kanban/kanban_record";

export class AutomationKanbanRecord extends KanbanRecord {
    addNewChild(params) {
        this.env.onAddActivity({
            context: {
                default_parent_id: this.props.record.data.id,
                default_trigger_type: params.trigger_type,
            },
        });
    }
}

AutomationKanbanRecord.Compiler = AutomationKanbanCompiler;
