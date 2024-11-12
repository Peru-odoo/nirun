/** @odoo-module */

import {fieldVisualFeedback} from "@web/views/fields/field";
import {FormLabel} from "@web/views/form/form_label";
import {patch} from "web.utils";

patch(FormLabel.prototype, "web_form_label_asterisk.isRequired", {
    get className() {
        const {invalid, empty, readonly, required} = fieldVisualFeedback(
            this.props.fieldInfo.FieldComponent,
            this.props.record,
            this.props.fieldName,
            this.props.fieldInfo
        );
        const classes = this.props.className ? [this.props.className] : [];
        if (invalid) {
            classes.push("o_field_invalid");
        }
        if (empty) {
            classes.push("o_form_label_empty");
        }
        if (readonly) {
            classes.push("o_form_label_readonly");
        }
        if (required) {
            classes.push("o_form_label_required");
        }
        return classes.join(" ");
    },
});
