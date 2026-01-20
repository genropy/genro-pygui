# Schema: Textual Widgets

## Abstract Elements

| Name | Sub Tags | Documentation |
| --- | --- | --- |
| `@widget` | `-` | - |

## Elements

| Name | Inherits | Sub Tags | Call Args | Compile | Documentation |
| --- | --- | --- | --- | --- | --- |
| `button` | - | - | `label, variant, tooltip, action, compact, flat` | `module: textual.widgets, class: Button` | A simple clickable button. |
| `checkbox` | - | - | `label, value, button_first, tooltip, compact` | `module: textual.widgets, class: Checkbox` | A check box widget that represents a boolean value. |
| `collapsible` | - | - | `children, title, collapsed, collapsed_symbol, expanded_symbol` | `module: textual.widgets, class: Collapsible` | A collapsible container. |
| `collapsibletitle` | - | - | `label, collapsed_symbol, expanded_symbol, collapsed` | `module: textual.widgets, class: CollapsibleTitle` | Title and symbol for the Collapsible. |
| `contentswitcher` | - | - | `children, initial` | `module: textual.widgets, class: ContentSwitcher` | A widget for switching between different children. |
| `datatable` | - | - | `show_header, show_row_labels, fixed_rows, fixed_columns, zebra_stripes, header_height, show_cursor, cursor_foreground_priority, cursor_background_priority, cursor_type, cell_padding` | `module: textual.widgets, class: DataTable` | A tabular widget that contains data. |
| `digits` | - | - | `value` | `module: textual.widgets, class: Digits` | A widget to display numerical values using a 3x3 grid of unicode characters. |
| `directorytree` | - | - | `path` | `module: textual.widgets, class: DirectoryTree` | A Tree widget that presents files and directories. |
| `footer` | - | - | `children, show_command_palette, compact` | `module: textual.widgets, class: Footer` | Textual Footer widget |
| `header` | - | - | `show_clock, icon, time_format` | `module: textual.widgets, class: Header` | A header widget with icon and clock. |
| `helppanel` | - | - | `children, markup` | `module: textual.widgets, class: HelpPanel` | - |
| `input` | - | - | `value, placeholder, password, restrict, type, max_length, valid_empty, select_on_focus, tooltip, compact` | `module: textual.widgets, class: Input` | A text input widget. |
| `keypanel` | - | - | `children, can_focus, can_focus_children, can_maximize` | `module: textual.widgets, class: KeyPanel` | - |
| `label` | - | - | `content, variant, expand, shrink, markup` | `module: textual.widgets, class: Label` | A simple label widget for displaying text-oriented renderables. |
| `link` | - | - | `text, url, tooltip` | `module: textual.widgets, class: Link` | A simple, clickable link that opens a URL. |
| `listitem` | - | - | `children, markup` | `module: textual.widgets, class: ListItem` | A widget that is an item within a `ListView`. |
| `listview` | - | - | `children, initial_index` | `module: textual.widgets, class: ListView` | A vertical list view widget. |
| `loadingindicator` | - | - | `id, classes, name, disabled` | `module: textual.widgets, class: LoadingIndicator` | Display an animated loading indicator. |
| `log` | - | - | `highlight, max_lines, auto_scroll` | `module: textual.widgets, class: Log` | A widget to log text. |
| `markdown` | - | - | `markdown, parser_factory, open_links` | `module: textual.widgets, class: Markdown` | Textual Markdown widget |
| `markdownviewer` | - | - | `markdown, show_table_of_contents, parser_factory, open_links` | `module: textual.widgets, class: MarkdownViewer` | A Markdown viewer widget. |
| `maskedinput` | - | - | `template, value, placeholder, valid_empty, select_on_focus, tooltip, compact` | `module: textual.widgets, class: MaskedInput` | A masked text input widget. |
| `optionlist` | - | - | `content, markup, compact` | `module: textual.widgets, class: OptionList` | A navigable list of options. |
| `placeholder` | - | - | `label, variant` | `module: textual.widgets, class: Placeholder` | A simple placeholder widget to use before you build your custom widgets. |
| `pretty` | - | - | `object` | `module: textual.widgets, class: Pretty` | A pretty-printing widget. |
| `progressbar` | - | - | `total, show_bar, show_percentage, show_eta, clock, gradient` | `module: textual.widgets, class: ProgressBar` | A progress bar widget. |
| `radiobutton` | - | - | `label, value, button_first, tooltip, compact` | `module: textual.widgets, class: RadioButton` | A radio button widget that represents a boolean value. |
| `radioset` | - | - | `buttons, tooltip, compact` | `module: textual.widgets, class: RadioSet` | Widget for grouping a collection of radio buttons into a set. |
| `richlog` | - | - | `max_lines, min_width, wrap, highlight, markup, auto_scroll` | `module: textual.widgets, class: RichLog` | A widget for logging Rich renderables and text. |
| `rule` | - | - | `orientation, line_style` | `module: textual.widgets, class: Rule` | A rule widget to separate content, similar to a `<hr>` HTML tag. |
| `select` | - | - | `options, prompt, allow_blank, value, type_to_search, tooltip, compact` | `module: textual.widgets, class: Select` | Widget to select from a list of possible options. |
| `selectionlist` | - | - | `selections, compact` | `module: textual.widgets, class: SelectionList` | A vertical selection list that allows making multiple selections. |
| `sparkline` | - | - | `data, min_color, max_color, summary_function` | `module: textual.widgets, class: Sparkline` | A sparkline widget to display numerical data. |
| `static` | - | - | `content, expand, shrink, markup` | `module: textual.widgets, class: Static` | A widget to display simple static content, or use as a base class for more complex widgets. |
| `switch` | - | - | `value, animate, tooltip` | `module: textual.widgets, class: Switch` | A switch widget that represents a boolean value. |
| `tab` | - | - | `label` | `module: textual.widgets, class: Tab` | A Widget to manage a single tab within a Tabs widget. |
| `tabbedcontent` | - | - | `titles, initial` | `module: textual.widgets, class: TabbedContent` | A container with associated tabs to toggle content visibility. |
| `tabpane` | - | - | `title, children` | `module: textual.widgets, class: TabPane` | A container for switchable content, with additional title. |
| `tabs` | - | - | `tabs, active` | `module: textual.widgets, class: Tabs` | A row of tabs. |
| `textarea` | - | - | `text, language, theme, soft_wrap, tab_behavior, read_only, show_cursor, show_line_numbers, line_number_start, max_checkpoints, tooltip, compact, highlight_cursor_line, placeholder` | `module: textual.widgets, class: TextArea` | Textual TextArea widget |
| `tooltip` | - | - | `content, expand, shrink, markup` | `module: textual.widgets, class: Tooltip` | Textual Tooltip widget |
| `tree` | - | - | `label, data` | `module: textual.widgets, class: Tree` | A widget for displaying and navigating data in a tree. |
| `welcome` | - | - | `content, expand, shrink, markup` | `module: textual.widgets, class: Welcome` | A Textual welcome widget. |