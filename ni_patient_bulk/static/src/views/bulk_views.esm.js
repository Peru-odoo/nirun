/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";

const {onWillStart, useComponent} = owl;

export function userBulkButton() {
    const component = useComponent();
    const user = useService("user");
    const action = useService("action");

    onWillStart(async () => {
        component.isManager = await user.hasGroup("ni_patient.group_manager");
    });

    component.onClickRegister = () => {
        action.doAction({
            name: "ผู้รับบริการ",
            type: "ir.actions.act_window",
            res_model: "ni.encounter.bulk",
            target: "new",
            views: [[false, "form"]],
        });
    };
}

export class PatientBulkListController extends ListController {
    setup() {
        super.setup();
        userBulkButton();
    }
}

registry.category("views").add("ni_patient_bulk_tree", {
    ...listView,
    Controller: PatientBulkListController,
    buttonTemplate: "ni_patient_bulk.ListView.buttons",
});

export class PatientBulkKanbanController extends KanbanController {
    setup() {
        super.setup();
        userBulkButton();
    }
}
registry.category("views").add("ni_patient_bulk_kanban", {
    ...kanbanView,
    Controller: PatientBulkKanbanController,
    buttonTemplate: "ni_patient_bulk.KanbanView.buttons",
});
