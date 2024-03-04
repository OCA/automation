/** @odoo-module **/
/* global Chart*/

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
                labels: this.props.value.done.map(function (pt) {
                    return pt.x;
                }),
                datasets: [
                    {
                        backgroundColor: "#4CAF5080",
                        borderColor: "#4CAF50",
                        data: this.props.value.done,
                        fill: "start",
                        label: this.env._t("Done"),
                        borderWidth: 2,
                    },
                    {
                        backgroundColor: "#F4433680",
                        borderColor: "#F44336",
                        data: this.props.value.error,
                        fill: "start",
                        label: this.env._t("Error"),
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
        Chart.animationService.advance();
    }
}

AutomationGraph.template = "automation_oca.AutomationGraph";
AutomationGraph.props = {
    ...standardFieldProps,
};

registry.category("fields").add("automation_graph", AutomationGraph);
