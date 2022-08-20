import threading
import time
from collections import OrderedDict
from typing import List, Tuple, Generator, Optional

import wandb
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from wandb.util import generate_id

from trecover.config import log
from trecover.train.collab.optim import AuxiliaryOptimizer
from trecover.utils.visualization import visualize_columns, visualize_target


# TODO from rich.status import Status


class CollaborativeVisualizer(object):
    def __init__(self,
                 aux_opt: AuxiliaryOptimizer,
                 delimiter: str = '',
                 visualize_every_step: int = 5,
                 refresh_period: int = 35,
                 delay_in_steps: int = 0,
                 delay_in_seconds: int = 180,
                 wandb_key: Optional[str] = None,
                 wandb_project: Optional[str] = None,
                 wandb_id: Optional[str] = None,
                 wandb_registry: Optional[str] = None):
        self.aux_opt = aux_opt
        self.delimiter = delimiter
        self.visualize_every_step = visualize_every_step
        self.last_performance_step = -1
        self.refresh_period = refresh_period
        self.steps_performance = OrderedDict()
        self.delay_in_steps = delay_in_steps
        self.delay_in_seconds = delay_in_seconds
        self.last_yield_step = -1
        self.last_yield_time = time.monotonic()
        self.wandb_report = wandb_key is not None
        self.finished = threading.Event()

        if self.wandb_report and wandb.run is None:
            wandb.login(key=wandb_key)

            if wandb_id is None:
                wandb_id = generate_id()

            wandb.init(
                project=wandb_project,
                name=wandb_id,
                id=wandb_id,
                dir=wandb_registry,
                resume='allow',
                anonymous='never'
            )

    def stream(self) -> Generator[Tuple[int, List[Panel]], None, None]:
        while not self.finished.is_set() or self.steps_performance:
            with self.aux_opt.transaction:
                if self._is_time_to_visualize:
                    if self._need_to_sync:
                        log.project_console.print(
                            'Need to synchronize this peer before visualization',
                            style='salmon1',
                            justify='right'
                        )
                        self.aux_opt.sync_state()

                    self.steps_performance[self.aux_opt.local_epoch - 1] = self.aux_opt.wrapped_model.perform()
                    self.last_performance_step = self.aux_opt.local_epoch

            if self._is_time_to_yield:
                step, step_performance = self.steps_performance.popitem(last=False)
                yield step, self._visualize(step_performance, step)

                self.last_yield_time = time.monotonic()
                self.last_yield_step = step

            log.project_console.print('Visualize progress...', style='cyan', justify='right')
            time.sleep(self.refresh_period)

    def start(self, attach: bool = False) -> None:
        if attach:
            self._visualize_in_background()
        else:
            visualizer_thread = threading.Thread(name='VisualizerThread',
                                                 target=self._visualize_in_background,
                                                 daemon=True)
            visualizer_thread.start()

    def set_finished(self) -> None:
        self.finished.set()

    @property
    def _is_time_to_visualize(self) -> bool:
        return (
                not self.finished.is_set()
                and self.aux_opt.global_epoch != self.last_performance_step
                and self.aux_opt.global_epoch != 0
                and self.visualize_every_step > 0
                and self.aux_opt.global_epoch % self.visualize_every_step == 0
        )

    @property
    def _need_to_sync(self) -> bool:
        return (
                self.aux_opt.local_epoch != self.aux_opt.global_epoch or
                self.aux_opt.original_allow_state_sharing and not self.aux_opt.allow_state_sharing
        )

    @property
    def _is_time_to_yield(self) -> bool:
        if len(self.steps_performance) == 0:
            return False
        if time.monotonic() - self.last_yield_time > self.delay_in_seconds:
            return True
        if len(self.steps_performance) > self.delay_in_steps:
            return True

        return False

    def _visualize(self, performance: List[Tuple[List[str], List[str], List[str]]], step: int) -> List[Panel]:
        visualizations = list()

        for idx, (columns, predicted, original) in enumerate(performance):
            columns = visualize_columns(columns, delimiter=self.delimiter, as_rows=True)
            predicted = visualize_target(predicted, delimiter=self.delimiter)
            original = visualize_target(original, delimiter=self.delimiter)

            columns = (Text(row, style='bright_blue', overflow='ellipsis', no_wrap=True) for row in columns)
            predicted = Text(predicted, style='cyan', justify='center', overflow='ellipsis')
            original = Text(original, justify='center', overflow='ellipsis')

            panel_group = Group(
                Text('Columns', style='magenta', justify='center'),
                *columns,
                Text('Predicted', style='magenta', justify='center'),
                predicted,
                Text('Original', style='magenta', justify='center'),
                original
            )

            visualizations.append(
                Panel(panel_group, title=f'Step {step:_}, example {idx + 1}',
                      title_align='left', border_style='magenta')
            )

        return visualizations

    def _visualize_in_background(self) -> None:
        log.project_console.print('Start visualizer', style='bright_blue', justify='right')

        try:
            self._visualizer_loop()

        except KeyboardInterrupt:
            log.project_console.print('Visualizer stopping...', style='yellow', justify='right')
        finally:
            self.set_finished()

            if self.steps_performance:
                log.project_console.print(f'Trying to report {len(self.steps_performance)} delayed visualizations...',
                                          style='yellow', justify='right')
                self.delay_in_seconds = 0
                self.refresh_period = 0
                self._visualizer_loop()

            log.project_console.print('Visualizer is stopped', style='yellow', justify='right')

            if self.wandb_report:
                wandb.finish()

    def _visualizer_loop(self) -> None:
        for step, step_visualizations in self.stream():
            for visualization in step_visualizations:
                log.project_console.print(visualization, justify='full')

            if self.wandb_report:
                with (wandb_recorder := Console(record=True)).capture():
                    for visualization in step_visualizations:
                        wandb_recorder.print(visualization, justify='full')

                wandb.log({'visualization': wandb.Html(wandb_recorder.export_html())}, step=step)
