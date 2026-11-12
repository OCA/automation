import {X2ManyField, x2ManyField} from "@web/views/fields/x2many/x2many_field";
import {useOpenX2ManyRecord, useX2ManyCrud} from "@web/views/fields/relational_utils";
import {AutomationKanbanCompiler} from "../../views/automation_kanban/automation_kanban_compiler.esm";
import {AutomationKanbanRenderer} from "../../views/automation_kanban/automation_kanban_renderer.esm";
import {registry} from "@web/core/registry";
import {useSubEnv} from "@odoo/owl";

export class AutomationActivity extends X2ManyField {
    setup() {
        super.setup();
        useSubEnv({
            onAddActivity: this.onAdd.bind(this),
        });
        const {saveRecord, updateRecord} = useX2ManyCrud(
            () => this.list,
            this.isMany2Many
        );
        const openRecord = useOpenX2ManyRecord({
            resModel: this.list.resModel,
            activeField: this.activeField,
            activeActions: this.activeActions,
            getList: () => this.list,
            saveRecord: async (record) => {
                await saveRecord(record);
                await this.props.record.save();
            },
            updateRecord,
            isMany2Many: this.isMany2Many,
        });
        this._openRecord = (params) => {
            const activeElement = document.activeElement;
            openRecord({
                ...params,
                controls: this.controls,
                onClose: async () => {
                    if (activeElement) {
                        activeElement.focus();
                    }
                    await this.props.record.save();
                    this.props.record.model.notify();
                },
            });
        };
    }

    // Since 19.0 the compiler is threaded through ``rendererProps`` (the
    // ``KanbanRecord.Compiler`` static attribute is no longer read), so we inject
    // our custom compiler here to keep the "add child activity" buttons working.
    get rendererProps() {
        const props = super.rendererProps;
        if (this.props.viewMode === "kanban") {
            props.Compiler = AutomationKanbanCompiler;
        }
        return props;
    }
}

AutomationActivity.components = {
    ...AutomationActivity.components,
    KanbanRenderer: AutomationKanbanRenderer,
};

export const AutomationActivityField = {...x2ManyField, component: AutomationActivity};
registry.category("fields").add("automation_step", AutomationActivityField);
