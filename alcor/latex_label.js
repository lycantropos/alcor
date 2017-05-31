// import {Label, LabelView} from "models/annotations/label"
//
// export class LatexLabelView extends LabelView
//   render: () ->
//     ctx = @plot_view.canvas_view.ctx
//
//     switch @model.angle_units
//       when "rad" then angle = -1 * @model.angle
//       when "deg" then angle = -1 * @model.angle * Math.PI/180.0
//
//     if @model.x_units == "data"
//       vx = @xmapper.map_to_target(@model.x)
//     else
//       vx = @model.x
//     sx = @canvas.vx_to_sx(vx)
//
//     if @model.y_units == "data"
//       vy = @ymapper.map_to_target(@model.y)
//     else
//       vy = @model.y
//     sy = @canvas.vy_to_sy(vy)
//
//     if @model.panel?
//       panel_offset = @_get_panel_offset()
//       sx += panel_offset.x
//       sy += panel_offset.y
//
//     @_css_text(ctx, "", sx + @model.x_offset, sy - @model.y_offset, angle)
//
//     katex.render(@model.text, @el, {displayMode: true})
//
// export class LatexLabel extends Label
//   type: 'LatexLabel'
//   default_view: LatexLabelView