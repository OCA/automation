/** @odoo-module */

import {AutomationKanbanRecord} from "./automation_kanban_record.esm";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";

export class AutomationKanbanRenderer extends KanbanRenderer {
    /*
    Here we are going to reorder the items in the proper way and
    we will show the items with the proper padding
    */
    getGroupsOrRecords() {
        return this._sortRecordsHierarchy(this.props.list.records, false).map(
            (record) => ({
                record,
                key: record.id,
            })
        );
    }
    _sortRecordsHierarchy(records, parent_id) {
        return records.flatMap((record) => {
            if (!record.data.id) {
                return [];
            }
            if (record.data.parent_id && record.data.parent_id[0] !== parent_id) {
                return [];
            }
            if (!record.data.parent_id && parent_id) {
                return [];
            }
            return [record, ...this._sortRecordsHierarchy(records, record.data.id)];
        });
    }
}

AutomationKanbanRenderer.components = {
    ...AutomationKanbanRenderer.components,
    KanbanRecord: AutomationKanbanRecord,
};
