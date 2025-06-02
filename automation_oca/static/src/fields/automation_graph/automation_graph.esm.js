/* @odoo-module */
/* global Chart*/

import {_t} from "@web/core/l10n/translation";
import {loadJS} from "@web/core/assets";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const {Component, onWillStart, useEffect, useRef} = owl;

export class AutomationGraph extends Component {
    setup() {
        this.chart = null;
        this.canvasRef = useRef("canvas");
        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));
        useEffect(() => {
            this.renderChart();
            return () => {
                if (this.chart) {
                    this.chart.destroy();
                }
            };
        });
    }
    _getChartConfig() {
        return {
            type: "line",
            data: {
                labels: this.props.record.data[this.props.name].done.map(function (pt) {
                    return pt.x;
                }),
                datasets: [
                    {
                        backgroundColor: "#4CAF5080",
                        borderColor: "#4CAF50",
                        data: this.props.record.data[this.props.name].done,
                        fill: "start",
                        label: _t("Done"),
                        borderWidth: 2,
                    },
                    {
                        backgroundColor: "#F4433680",
                        borderColor: "#F44336",
                        data: this.props.record.data[this.props.name].error,
                        fill: "start",
                        label: _t("Error"),
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                plugins: {
                    legend: {display: false},
                },
                layout: {
                    padding: {left: 10, right: 10, top: 10, bottom: 10},
                },
                scales: {
                    y: {
                        type: "linear",
                        display: false,
                        beginAtZero: true,
                    },
                    x: {
                        ticks: {
                            maxRotation: 0,
                        },
                    },
                },
                maintainAspectRatio: false,
                elements: {
                    line: {
                        tension: 0.000001,
                    },
                },
                tooltips: {
                    intersect: false,
                    position: "nearest",
                    caretSize: 0,
                    borderWidth: 2,
                },
            },
        };
    }
    renderChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        var config = this._getChartConfig();
        this.chart = new Chart(this.canvasRef.el, config);
    }
}

AutomationGraph.template = "automation_oca.AutomationGraph";
AutomationGraph.props = {
    ...standardFieldProps,
};

export const AutomationGraphField = {component: AutomationGraph};
registry.category("fields").add("automation_graph", AutomationGraphField);
