#!/usr/bin/env python

# Copyright 2019 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from grafanalib import core as g
import defaults as d

QUANTILES = [0.99, 0.9, 0.5]


def show_quantiles(queryTemplate, quantiles=None, legend=""):
    quantiles = quantiles or QUANTILES
    targets = []
    for quantile in quantiles:
        q = "{:.2f}".format(quantile)
        l = legend or q
        targets.append(g.Target(expr=queryTemplate.format(quantile=q), legendFormat=l))
    return targets


NETWORK_PROGRAMMING_PANEL = [
    d.Graph(
        title="SLI: Network programming latency",
        description=(
            "NetworkProgrammingLatency is defined as the time it took to "
            + "program the network - from the time  the service or pod has "
            + "changed to the time the change was propagated and the proper "
            + "kube-proxy rules were synced. Exported for each endpoints object "
            + "that were part of the rules sync."
        ),
        targets=show_quantiles(
            (
                "quantile_over_time("
                + "0.99, "
                + 'kubeproxy:kubeproxy_network_programming_duration:histogram_quantile{{quantile="{quantile}"}}[24h])'
            ),
            legend="{{quantile}}",
        ),
        yAxes=g.single_y_axis(format=g.SECONDS_FORMAT),
    ),
    d.Graph(
        title="Network programming latency",
        description=(
            "NetworkProgrammingLatency is defined as the time it took to "
            + "program the network - from the time  the service or pod has "
            + "changed to the time the change was propagated and the proper "
            + "kube-proxy rules were synced. Exported for each endpoints object "
            + "that were part of the rules sync."
        ),
        targets=show_quantiles(
            'kubeproxy:kubeproxy_network_programming_duration:histogram_quantile{{quantile="{quantile}"}}',
            legend="{{quantile}}",
        ),
        yAxes=g.single_y_axis(format=g.SECONDS_FORMAT),
    ),
    d.Graph(
        title="kube-proxy: sync rules duation",
        description="Latency of one round of kube-proxy syncing proxy rules.",
        targets=show_quantiles(
            "histogram_quantile({quantile}, sum(rate(kubeproxy_sync_proxy_rules_duration_seconds_bucket[5m])) by (le))"
        ),
        yAxes=g.single_y_axis(format=g.SECONDS_FORMAT),
    ),
    d.simple_graph(
        "kube-proxy: rate of service changes",
        "sum(rate(kubeproxy_sync_proxy_rules_service_changes_total[5m]))",
        description="Rate of service changes that the proxy has seen over 5m",
        legend="rate",
    ),
    d.simple_graph(
        "kube-proxy: pending service changes",
        "sum(kubeproxy_sync_proxy_rules_service_changes_pending)",
        description="Number of pending service changes that have not yet been synced to the proxy.",
        legend="pending changes",
    ),
    d.simple_graph(
        "kube-proxy: rate of endpoint changes",
        "sum(rate(kubeproxy_sync_proxy_rules_endpoint_changes_total[5m]))",
        description="Rate of endpoint changes that the proxy has seen over 5m",
        legend="rate",
    ),
    d.simple_graph(
        "kube-proxy: pending endpoint changes",
        "sum(kubeproxy_sync_proxy_rules_endpoint_changes_pending)",
        description="Number of pending endpoint changes that have not yet been synced to the proxy.",
        legend="pending changes",
    ),
]

NETWORK_LATENCY_PANEL = [
    d.Graph(
        title="Network latency",
        targets=show_quantiles(
            'probes:in_cluster_network_latency:histogram_quantile{{quantile="{quantile}"}}',
            legend="{{quantile}}",
        ),
        yAxes=g.single_y_axis(format=g.SECONDS_FORMAT),
    )
]


dashboard = d.Dashboard(
    title="Network",
    rows=[
        d.Row(title="Network progamming latency", panels=NETWORK_PROGRAMMING_PANEL),
        d.Row(title="In-cluster network latency", panels=NETWORK_LATENCY_PANEL),
    ],
).auto_panel_ids()
