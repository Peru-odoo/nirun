/** @odoo-module **/

import {areDateEquals, formatDate, formatDateTime} from "@web/core/l10n/dates";
import {DateField} from "@web/views/fields/date/date_field";
import {localization} from "@web/core/l10n/localization";
import {patch} from "web.utils";

patch(DateField.prototype, "l10n_th_web_buddhist_calendar.date_field", {
    get formattedValue() {
        /** This method will only be called when field state is Read-Only . otherwise this have no affect **/
        let date = this.props.value;
        if (date.locale === "th-TH") {
            date = date.plus({year: 543});
        }
        return this.isDateTime ? formatDateTime(date, {format: localization.dateFormat}) : formatDate(date);
    },
    onDateTimeChanged(date) {
        /** This method will be called by bootstrapDateTimePicker when user select new value,
        the input 'date' will be in buddhist format.  **/
        if (!areDateEquals(this.date || "", date)) {
            if (date.locale === "th-TH") {
                this.props.update(date.minus({years: 543}));
            } else {
                this.props.update(date);
            }
        }
    },
});
