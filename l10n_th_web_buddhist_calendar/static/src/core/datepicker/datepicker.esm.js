/** @odoo-module **/

import {luxonToMoment, luxonToMomentFormat} from "@web/core/l10n/dates";
import {DatePicker} from "@web/core/datepicker/datepicker";
import {patch} from "web.utils";
import {session} from "@web/session";

/* eslint-disable */
const {DateTime} = luxon;
/* eslint-enable */

patch(DatePicker.prototype, "l10n_th_web_buddhist_calendar.datepicker", {
    updateInput({useStatic} = {}) {
        /*
        Will be called when field is not on Read-Only state
        'this.date' was updated by this.props.update() at Date{Time}Field.onDateTimeChanged(date)
        */
        let date = this.date;
        if (date.locale === "th-TH") {
            // FormattedDate will be different from commonDate when it is Thai Locale
            date = date.plus({year: 543});
        }
        const [commonDate] = this.formatValue(this.date, this.getOptions(useStatic));
        const [formattedDate] = this.formatValue(date, this.getOptions(useStatic));

        if (formattedDate !== null) {
            this.inputRef.el.value = formattedDate; // Update display format of DatePicker's input (Not on calendar picker)
            this.props.onUpdateInput(commonDate); // Update at Widget level with CE date
        }
    },

    bootstrapDateTimePicker(commandOrParams) {
        /*
            Before open BS-DatetimePicker we plus date with 543 years
            and also call getDefaultDate() when field have no default value
        */
        if (typeof commandOrParams === "object") {
            var locale = commandOrParams.locale || session.user_context.lang.replace("_", "-");
            var date = this.date;
            if (date && locale === "th-TH") {
                console.log(date);
                date = date.plus({year: 543});
            }
            const params = {
                ...commandOrParams,
                date: date || this.getDefaultDate(commandOrParams),
                format: luxonToMomentFormat(this.staticFormat),
                locale: commandOrParams.locale || (this.date && this.date.locale),
            };
            for (const prop in params) {
                if (params[prop] instanceof DateTime) {
                    params[prop] = luxonToMoment(params[prop]);
                }
            }
            commandOrParams = params;
        }

        window.$(this.rootRef.el).datetimepicker(commandOrParams);
    },
    getDefaultDate(commandOrParams) {
        /**
            We need to return default value as BE to BS DateTimePicker. Otherwise, user will start with CE input then
            all process will be ruin
        **/
        var locale = commandOrParams.locale || session.user_context.lang.replace("_", "-");
        if (this.date === false && locale === "th-TH") {
            return DateTime.now().plus({year: 543});
        }
        return null;
    },
});
