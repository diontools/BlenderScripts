import bpy
import blf

# 前回の選択オブジェクトと頂点数を記録する
previous_object_name = ''
previous_vertices_count = 0

# メッセージ表示ハンドル
draw_handle = None

def render_message(message):
    blf.size(0, 20)
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, 6, 0, 0, 0, 1)
    
    region = bpy.context.region
    (width, height) = blf.dimensions(0, message)
    
    blf.position(0, region.width - width - 20, 20, 0)
    blf.draw(0, message)

def remove_message():
    global draw_handle
    if draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handle, 'WINDOW')
        draw_handle = None

def show_message(message):
    global draw_handle
    remove_message()
    draw_handle = bpy.types.SpaceView3D.draw_handler_add(render_message, (message,), 'WINDOW', 'POST_PIXEL')

def get_verts_from_stat():
    stat = bpy.context.scene.statistics(bpy.context.view_layer)
    #print(stat)
    
    lang = bpy.context.preferences.view.language
    title = "頂点" if lang == "ja_JP" else "Verts"
    
    title_index = stat.find(title)
    if title_index < 0:
        return 0
    
    split_index = stat.find("/", title_index + 2)
    if split_index < 0:
        return 0
    
    end_index = stat.find(" ", split_index + 1)
    if end_index < 0:
        return 0
    
    return int(stat[split_index + 1 : end_index].replace(',', ''))

def reset_states():
    global previous_object_name
    global previous_vertices_count
    previous_object_name = ''
    previous_vertices_count = 0

def handler(scene):
    global previous_object_name
    global previous_vertices_count

    remove_message()

    # skip    
    if bpy.context.mode != "EDIT_MESH":
        reset_states()
        return

    # skip
    if not bpy.context.scene.tool_settings.use_mesh_automerge:
        reset_states()
        return
    
    obj = bpy.context.object

    if obj.type != "MESH":
        reset_states()
        return
    
    vertices_count = get_verts_from_stat()
    #print(f"handler {obj.name}, {vertices_count}, {previous_object_name}, {previous_vertices_count}")
    
    if previous_object_name == obj.name:
        if previous_vertices_count != vertices_count:
            print(f"頂点変化 {obj.name} ({previous_vertices_count} -> {vertices_count})")
            if previous_vertices_count > vertices_count:
                show_message(f"⚠️自動マージが有効の状態で頂点数が減少 ({vertices_count - previous_vertices_count} | {previous_vertices_count} → {vertices_count}) しました。大丈夫そ？")
    else:
        print(f"選択変更 {previous_object_name} -> {obj.name}")
    
    previous_object_name = obj.name
    previous_vertices_count = vertices_count

# ハンドラを登録
bpy.app.handlers.depsgraph_update_post.append(handler)

print("頂点変化の監視を開始しました。")
