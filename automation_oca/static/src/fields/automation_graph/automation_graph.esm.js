/** @odoo-module **/
/* global Chart*/
import {Component, onWillStart, useEffect, useRef} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {loadBundle} from "@web/core/assets";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class AutomationGraph extends Component {
    setup() {
        this.chart = null;
        this.canvasRef = useRef("canvas");
        onWillStart(async () => await loadBundle("web.chartjs_lib"));
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
                // Labels: this.props.value.done.map(function (pt) {
                //     return pt.x;
                // }),
                labels: this.props.record.data.graph_data.done.map(function (pt) {
                    return pt.x;
                }),
                datasets: [
                    {
                        backgroundColor: "#4CAF5080",
                        borderColor: "#4CAF50",
                        data: this.props.record.data.graph_data.done,
                        fill: "start",
                        label: _t("Done"),
                        borderWidth: 2,
                    },
                    {
                        backgroundColor: "#F4433680",
                        borderColor: "#F44336",
                        data: this.props.record.data.graph_data.error,
                        fill: "start",
                        label: _t("Error"),
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                legend: {display: false},

                layout: {
                    padding: {left: 10, right: 10, top: 10, bottom: 10},
                },
                scales: {
                    yAxes: [
                        {
                            type: "linear",
                            display: false,
                            ticks: {
                                beginAtZero: true,
                            },
                        },
                    ],
                    xAxes: [
                        {
                            ticks: {
                                maxRotation: 0,
                            },
                        },
                    ],
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
        // Chart.animationService.advance();
    }
}

AutomationGraph.template = "automation_oca.AutomationGraph";
AutomationGraph.props = {
    ...standardFieldProps,
};

registry.category("fields").add("automation_graph", {component: AutomationGraph});
