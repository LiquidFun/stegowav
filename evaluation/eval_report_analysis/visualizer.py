from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import textwrap


class EvalReportVisualizer:

    def __init__(self):
        pass

    def draw_pandas_barh(
            self,
            values_dict: Dict[str, Dict[str, int]],
            filename: str,
            graph_height: int,
            show_y_labels: bool = True):

        data, percentage, bar_labels, y_labels = self.__prepare_plot_data(values_dict)

        for index, label in enumerate(bar_labels):
            bar_labels[index] = textwrap.fill(label, width = 11)

        data_frame = pd.DataFrame(data = data, columns = bar_labels)

        ax = data_frame.plot.barh(stacked = True, figsize = (12, graph_height), cmap = 'tab20')
        ax.set_xlim(xmin = 0.0, xmax = 1.19)

        bar_labels = self.__generate_bar_labels(data)

        for label_index, label in enumerate(ax.patches):

            if bar_labels[label_index] > 0:
                label_text = f'{bar_labels[label_index]}%'

                annotation_x = label.get_x() + (label.get_width() / 2)
                annotation_y = label.get_y() + (label.get_height() / 2)

                annotation_xy = (annotation_x, annotation_y)

                ax.annotate(
                    label_text,
                    xy = annotation_xy,
                    horizontalalignment = 'center',
                    verticalalignment = 'center'
                )

        ax.set_xlabel('Gesamtanteil in Prozent')
        if show_y_labels:
            ax.set_ylabel('Kategorie')

        ax.xaxis.set_major_formatter(lambda x, pos: f'{round(x * 100)}%')
        plt.yticks(range(len(y_labels)), y_labels)

        plt.tight_layout()
        plt.savefig(f'graphs/{filename}', dpi = 500)

    @staticmethod
    def __prepare_plot_data(values_dict: Dict[str, Dict[str, int]]) -> \
            Tuple[List[List[int]], List[List[int]], List[str], List[str]]:

        y_labels: List[str] = [label for label in values_dict]

        for index, y_label in enumerate(y_labels):
            y_labels[index] = textwrap.fill(y_label, width = 15)

        all_rows = [list(values_dict[row].values()) for row in values_dict]

        percentages: List[List[int]] = []
        x_labels: List[str] = []

        for value in values_dict:
            row_percentages: List[int] = []

            row_sum = sum(list(values_dict[value].values()))

            for column in values_dict[value]:
                row_percentages.append(round(values_dict[value][column] / row_sum * 100))

                if column not in x_labels:
                    x_labels.append(column)

            percentages.append(row_percentages)

        return all_rows, percentages, x_labels, y_labels

    @staticmethod
    def __generate_bar_labels(data: List[List[int]]) -> List[int]:
        labels = []
        for row in data:
            labels_row = []
            for entry in row:
                labels_row.append(round(entry * 100))

            labels.append(labels_row)

        # adjust labels that are the nearest to a .5 so the sum is 100
        for row_index, row in enumerate(labels):
            row_sum = sum(row)

            if row_sum != 100:
                difference = row_sum - 100
                values_sum_too_high = difference > 0
                abs_difference = abs(difference)

                modulo_differences = [value % 1 for value in data[row_index]]
                rounding_differences = [value - 0.5 for value in modulo_differences]

                for x in range(abs_difference):

                    if values_sum_too_high:
                        for index, rounding_difference in enumerate(rounding_differences):
                            if rounding_difference < 0:
                                rounding_differences[index] = 0

                        extreme_value_index = rounding_differences.index(min(rounding_differences))
                        labels[row_index][extreme_value_index] -= 1
                    else:
                        for index, rounding_difference in enumerate(rounding_differences):
                            if rounding_difference > 0:
                                rounding_differences[index] = 0

                        extreme_value_index = rounding_differences.index(max(rounding_differences))
                        labels[row_index][extreme_value_index] += 1

        # It's not actually flattened, more like a column-wise flattening
        flattened_labels: List[int] = []
        row_lengths = [len(row) for row in labels]

        for column_index in range(max(row_lengths)):
            for label in labels:
                flattened_labels.append(label[column_index])

        if sum(flattened_labels) != 100 * len(data):
            print(f'Warning: bar label sum is not {100 * len(data)} ({sum(flattened_labels)})')

        return flattened_labels
