import {Component} from "@odoo/owl";
import {FileUploader} from "@web/views/fields/file_handler";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {useService} from "@web/core/utils/hooks";

export class AutomationFileUploader extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
    }
    async onFileUploaded(file) {
        const action = await this.orm.call(
            "automation.configuration",
            "create_document_from_attachment",
            ["", file.data],
            {context: {...this.extraContext, ...this.env.searchModel.context}}
        );
        if (action.context && action.context.notifications) {
            for (const [title, msg] of Object.entries(action.context.notifications)) {
                this.notification.add(msg, {
                    title: title,
                    type: "info",
                    sticky: true,
                });
            }
            delete action.context.notifications;
        }
        this.action.doAction(action);
    }
}
AutomationFileUploader.components = {
    FileUploader,
};
AutomationFileUploader.template = "automation_oca.AutomationFileUploader";
AutomationFileUploader.props = {
    ...standardWidgetProps,
    record: {type: Object, optional: true},
    slots: {type: Object, optional: true},
    acceptedFileExtensions: {type: String, optional: true},
};
AutomationFileUploader.defaultProps = {
    acceptedFileExtensions: ".json",
};

export const automationFileUploader = {
    component: AutomationFileUploader,
};

registry
    .category("view_widgets")
    .add("automation_oca_file_uploader", automationFileUploader);

export class AutomationKanbanController extends KanbanController {}
AutomationKanbanController.components = {
    ...KanbanController.components,
    AutomationFileUploader,
};

export const AutomationKanbanView = {
    ...kanbanView,
    Controller: AutomationKanbanController,
    buttonTemplate: "automation_oca.KanbanView.Buttons",
};

registry.category("views").add("automation_upload_kanban", AutomationKanbanView);
