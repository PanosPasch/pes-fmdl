import bpy
import decimal
import struct
import bmesh
from math import radians
import mathutils
import binascii
import string
import os.path

def read_some_data(context, filepath, use_some_setting, self):
    print("running read_some_data...")
    f = open(filepath, 'rb')
    data = f.read()
    f.close()

    # would normally load the data here
    if (check_magic(data[0x0:0x4]) != 1):
        print('Returned not true')
        return{'CANCELLED'}
    
    version = read_float(data[0x4:0x8])
    
    blocks_offset = read_uint64(data[0x8:0x10])
    
    section0_bflags = read_uint64(data[0x10:0x18])
    section1_bflags = read_uint64(data[0x18:0x20])
    
    section0_bcount = read_uint(data[0x20:0x24])
    section1_bcount = read_uint(data[0x24:0x28])
    
    section0_offset = read_uint(data[0x28:0x2C])
    section0_length = read_uint(data[0x2C:0x30])
    
    section1_offset = read_uint(data[0x30:0x34])
    section1_length = read_uint(data[0x34:0x38])
    
    section0_blocks = []
    for i in range(1, section0_bcount+1):
        offset = blocks_offset+(0x8*(i-1))
        block_id = read_ushort(data[offset:offset+0x2])
        block_entries = read_ushort(data[offset+0x2:offset+0x4])
        block_offset = read_uint(data[offset+0x4:offset+0x8])
        section0_blocks.append([block_id, block_entries, block_offset])
        
    section1_blocks = []
    for i in range(1, section1_bcount+1):
        offset = blocks_offset+(section0_bcount*0x8)+(0xC*(i-1))
        #print('This is section 1 block {0} at {1}'.format(i,offset))
        block_id = read_uint(data[offset:offset+0x4])
        block_offset = read_uint(data[offset+0x4:offset+0x8])
        block_length = read_uint(data[offset+0x8:offset+0xC])
        section1_blocks.append([block_id, block_offset, block_length])
        
    bone_definitions = []
    mesh_group_definitions = []
    mesh_group_assignments = []
    mesh_information = []
    material_instance = []
    bone_group_definitions = []
    texture_definitions = []
    texture_type_assignments = []
    material_type_assignments = []
    mesh_format_assignments = []
    mesh_format_definitions = []
    vertex_format_definitions = []
    string_definitions = []
    bounding_box_definitions = []
    buffer_offset_definitions = []
    lod_face_info = []
    face_index_definitions = []
    unknown_block_1 = []
    unknown_block_2 = []
    texture_path_hash_definitions = []
    string_hash_definitions = []
    material_parameters = []
    vertex_buffer = []
    strings = []
        
    for block in section0_blocks:
        block_id = block[0]
        offset = section0_offset+block[2]
        count = block[1]
        for i in range(1, count+1):
            if (block_id == 0):
                leng = 0x30
                data_offset = offset+(leng*(i-1))
                bone_definitions.append(read_bone_definitions(data[data_offset:data_offset+leng]))                
            if (block_id == 1):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                mesh_group_definitions.append(read_mesh_group_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 2):
                leng = 0x20
                data_offset = offset+(leng*(i-1))
                mesh_group_assignments.append(read_mesh_group_assignments(data[data_offset:data_offset+leng]))
            if (block_id == 3):
                leng = 0x30
                data_offset = offset+(leng*(i-1))
                mesh_information.append(read_mesh_information(data[data_offset:data_offset+leng]))
            if (block_id == 4):
                leng = 0x10
                data_offset = offset+(leng*(i-1))
                material_instance.append(read_material_instance(data[data_offset:data_offset+leng]))
            if (block_id == 5):
                leng = 0x44
                data_offset = offset+(leng*(i-1))
                bone_group_definitions.append(read_bone_group_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 6):
                leng = 0x4
                data_offset = offset+(leng*(i-1))
                texture_definitions.append(read_texture_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 7):
                leng = 0x4
                data_offset = offset+(leng*(i-1))
                texture_type_assignments.append(read_texture_type_assignments(data[data_offset:data_offset+leng]))
            if (block_id == 8):
                leng = 0x4
                data_offset = offset+(leng*(i-1))
                material_type_assignments.append(read_material_type_assignments(data[data_offset:data_offset+leng]))
            if (block_id == 9):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                mesh_format_assignments.append(read_mesh_format_assignments(data[data_offset:data_offset+leng]))
            if (block_id == 10):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                mesh_format_definitions.append(read_mesh_format_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 11):
                leng = 0x4
                data_offset = offset+(leng*(i-1))
                vertex_format_definitions.append(read_vertex_format_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 12):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                string_definitions.append(read_string_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 13):
                leng = 0x20
                data_offset = offset+(leng*(i-1))
                bounding_box_definitions.append(read_bounding_box_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 14):
                leng = 0x10
                data_offset = offset+(leng*(i-1))
                buffer_offset_definitions.append(read_buffer_offset_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 16):
                leng = 0x10
                data_offset = offset+(leng*(i-1))
                lod_face_info.append(read_lod_face_info(data[data_offset:data_offset+leng]))
            if (block_id == 17):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                face_index_definitions.append(read_face_index_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 18):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                unknown_block_1.append(read_unknown_block_1(data[data_offset:data_offset+leng]))
            if (block_id == 20):
                leng = 0x80
                data_offset = offset+(leng*(i-1))
                unknown_block_2.append(read_unknown_block_2(data[data_offset:data_offset+leng]))
            if (block_id == 21):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                texture_path_hash_definitions.append(read_texture_path_hash_definitions(data[data_offset:data_offset+leng]))
            if (block_id == 22):
                leng = 0x8
                data_offset = offset+(leng*(i-1))
                string_hash_definitions.append(read_string_hash_definitions(data[data_offset:data_offset+leng]))
    
    for block in section1_blocks:
        block_id = block[0]
        offset = section1_offset+block[1]
        length = block[2]
        if (block_id == 0):
            material_parameters.append(read_material_parameters(data[offset:offset+length]))
        if (block_id == 2):
            #print(buffer_offset_definitions)
            vertex_buffer = read_vertex_buffer(data[offset:offset+length], buffer_offset_definitions)
        if (block_id == 3):
            strings.append(read_strings(data[offset:offset+length], string_definitions))
            
    for tex_i in texture_definitions:
        tex_i.append(strings[0][0][tex_i[0]])
                
    #print(len(mesh_information))
    #Create Bones
    have_bones = False
    if (len(bone_definitions) > 0):
        have_bones = True
        bpy.ops.object.add(
            type='ARMATURE',
            enter_editmode=True)
        ob = bpy.context.object
        ob.show_x_ray = False
        ob.name = "Skeleton"
        amt = ob.data
        amt.name = "SkeletonAmt"
        amt.show_axes = True
        bpy.ops.object.mode_set(mode='EDIT')
        
    for bon in bone_definitions:
        title = strings[0][0][bon[0]]
        parent_id = bon[1]
        local_x = bon[4]
        local_y = bon[5]
        local_z = bon[6]
        local_w = bon[7]
        world_x = bon[8]
        world_y = bon[9]
        world_z = bon[10]
        world_w = bon[11]
        print("X:{0}, Y:{1}, Z:{2}, W:{3}, X:{4}, Y:{5}, Z:{6}, W:{7}".format(local_x,local_y,local_z,local_w,world_x,world_y,world_z,world_w))
        #quat = mathutils.Quaternion([local_w, local_x, local_y, local_z])
        #quat1 = mathutils.Quaternion([world_w, world_x, world_y, world_z])        
        bone = amt.edit_bones.new(title)
        if (parent_id != 65535):
            parent = amt.edit_bones[parent_id]
            bone.parent = parent
            #bone.head = parent.tail
            #print(quat.to_matrix()[0])
            bone.use_connect = False
        #else:
            #bone.head = (0,0,0) 
            #print(quat.to_matrix()[0])
        bone.head = (bone.head[0]+world_x,bone.head[1]+world_y,bone.head[2]+world_z)
        bone.tail = (local_x+bone.head[0], local_y+bone.head[1], local_z+bone.head[2])
        #print(quat1.to_matrix()[0])
    if (have_bones):
        bpy.ops.object.mode_set(mode='OBJECT')
        ob.rotation_euler = (radians(90), 0, 0)
    #Create Bone Groups
#    if (len(bone_group_definitions) > 0):
#        for bn_grp in bone_group_definitions:
#            bone_group = ob.pose.bone_groups.new()
#            print(bn_grp)
#            for bonid in bn_grp[2]:
#                title = strings[0][0][bone_definitions[bonid][0]]
#                print(title)
#                for bn in ob.pose.bones:
#                    if (bn.name == title):
#                        bn.bone_group = bone_group
    #Create Mesh Groups
    ##we need to deselect and make inactive all objects in order to have correctly assigned objects
    bpy.context.scene.objects.active = None
    for obj_old in bpy.data.objects:
        obj_old.select = False
    for grp in mesh_group_definitions:
        bpy.ops.group.create(name="{0}".format(read_string(strings[0][0][grp[0]])))
    #Create Materials
    for mtr in material_instance:
        mat_name = read_string(strings[0][0][mtr[0]])
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
        links = mat.node_tree.links
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        node_output.location = 400,0
        link = links.new(principled.outputs[0], node_output.inputs[0])
        for tex in range(mtr[4], mtr[4]+mtr[2]):
            tex_type = read_string(strings[0][0][texture_type_assignments[tex][0]])
            print(tex_type)
            image_tex = nodes.new(type='ShaderNodeTexImage')
            image_name = read_string(strings[0][0][texture_definitions[texture_type_assignments[tex][1]][0]])
            image_path = read_string(strings[0][0][texture_definitions[texture_type_assignments[tex][1]][1]])
            if (not os.path.isdir(image_path)):
                msg = "Please select a dir for path {0}".format(image_path)
                print(image_path)
                #DO SOMETHING TO GET NEW CUSTOM PATH FROM USER
                image_path = input('Enter new path:')
                strings[0][0][texture_definitions[texture_type_assignments[tex][1]][1]] = image_path
                #image_path = new_path_from_user
            image_full_dir = '{0}{1}'.format(image_path,image_name)
            print(image_full_dir)
            try:
                image_tex.image = bpy.data.images.load(image_path+image_name.replace('.tga','.dds'), check_existing=True)
            except:
                image_tex.image = bpy.data.images.new(image_name, 1, 1)
            if (tex_type == 'Base_Tex_SRGB'):
                image_tex.color_space = 'COLOR'
                mix_shader = nodes.new(type='ShaderNodeMixShader')
                transparent_bsdf = nodes.new(type='ShaderNodeBsdfTransparent')
                link = links.new(image_tex.outputs[0], principled.inputs[0])
                link = links.new(image_tex.outputs[1], mix_shader.inputs[0])
                link = links.new(principled.outputs[0], mix_shader.inputs[2])
                link = links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])
                link = links.new(mix_shader.outputs[0], node_output.inputs[0])
            elif (tex_type == 'NormalMap_Tex_NRM'):
                image_tex.color_space = 'NONE'
                bump_shader = nodes.new(type='ShaderNodeBump')
                seperate_rgb = nodes.new(type='ShaderNodeSeparateRGB')
                link = links.new(image_tex.outputs['Color'], seperate_rgb.inputs[0])
                link = links.new(seperate_rgb.outputs['G'], bump_shader.inputs['Strength'])                
                link = links.new(image_tex.outputs['Alpha'], bump_shader.inputs['Height'])
                link = links.new(bump_shader.outputs[0], principled.inputs['Normal'])
            elif (tex_type == 'SpecularMap_Tex_LIN'):
                image_tex.color_space = 'NONE'
                seperate_rgb = nodes.new(type='ShaderNodeSeparateRGB')
                link = links.new(image_tex.outputs[0], seperate_rgb.inputs[0])
                link = links.new(seperate_rgb.outputs['G'], principled.inputs[5])
            elif (tex_type == 'Translucent_Tex_LIN'):
                image_tex.color_space = 'NONE'
            elif (tex_type == 'RoughnessMap_Tex_LIN'):
                image_tex.color_space = 'NONE'
                seperate_rgb = nodes.new(type='ShaderNodeSeparateRGB')
                link = links.new(image_tex.outputs[0], seperate_rgb.inputs[0])
                link = links.new(seperate_rgb.outputs['R'], principled.inputs[7])
            elif (tex_type == 'CubeMap_Tex_LIN'):
                image_tex.color_space = 'NONE'
            elif (tex_type == 'Mask_Tex_LIN'):
                image_tex.color_space = 'NONE'
            elif (tex_type == 'SubNormalMap_Tex_NRM'):
                image_tex.color_space = 'NONE'
            elif (tex_type == 'MetalnessMap_Tex_LIN'):
                image_tex.color_space = 'NONE'      
                link = links.new(image_tex.outputs[0], principled.inputs[4])          
        for param in range(mtr[5], mtr[5]+mtr[3]):
            param_type = read_string(strings[0][0][texture_type_assignments[param][0]])
            print(param_type)
    #Create Meshes
    mesh_group_index = 0 #prepare for mesh grouping
    mesh_group_obj_count = mesh_group_assignments[mesh_group_index][1]
    for i in range(0, len(mesh_information)):
        vertex_count = mesh_information[i][5]
        face_count = mesh_information[i][7]
        face_start = mesh_information[i][6]
        mesh_format_count = mesh_format_assignments[i][0]
        mesh_format_start = mesh_format_assignments[i][3]
        vertex_format_count = mesh_format_assignments[i][1]
        vertex_format_start = mesh_format_assignments[i][4]
        vertices = []
        normals = []
        indices = []
        bone_weights = []
        bone_indices = []
        uv0 = []
        uv1 = []
        uv2 = []
        uv3 = []
        faces = []
        #print('Mesh: {0}, Start: {1}, Count: {2}'.format(i, mesh_format_start, mesh_format_count))
        for f in range(0, (face_count//3)):
            #print('Face {0}:{1}'.format(f,vertex_buffer[2][(face_start*2)+(6*f):(face_start*2)+(6*f)+2]))
            #print('Face {0}:{1}'.format(f,vertex_buffer[2][(face_start*2)+(6*f)+2:(face_start*2)+(6*f)+4]))
            #print('Face {0}:{1}'.format(f,vertex_buffer[2][(face_start*2)+(6*f)+4:(face_start*2)+(6*f)+6]))                        
            ver_1 = read_ushort(vertex_buffer[2][(face_start*2)+(6*f):(face_start*2)+(6*f)+2])
            ver_2 = read_ushort(vertex_buffer[2][(face_start*2)+(6*f)+2:(face_start*2)+(6*f)+4])
            ver_3 = read_ushort(vertex_buffer[2][(face_start*2)+(6*f)+4:(face_start*2)+(6*f)+6])
            faces.append([ver_1,ver_2,ver_3])
        for z in range(mesh_format_start, mesh_format_start+mesh_format_count):
            #print(z)
            mesh_def = mesh_format_definitions[z]
            chunk = mesh_def[0]
            entry_len = mesh_def[2]
            entry_count = mesh_def[1]
            entry_offset = mesh_def[4]
            for j in range(vertex_format_start, vertex_format_start+entry_count):
                #print(j)
                ver_def = vertex_format_definitions[j]
                usage = ver_def[0]
                type = ver_def[1]
                offset = ver_def[2]
                #print(offset)
                for ver in range(0, vertex_count):
                    if (usage == 0):
                        ver_x = read_float(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+4])
                        ver_y = read_float(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+4:entry_offset+(ver*entry_len)+offset+8])
                        ver_z = read_float(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+8:entry_offset+(ver*entry_len)+offset+12])
                        vertices.append([ver_x, ver_y, ver_z])
                    if (usage == 1):
                        #print('Address: {0}'.format(entry_offset+(ver*entry_len)+offset))
                        weight_0 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+1])/255
                        weight_1 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+1:entry_offset+(ver*entry_len)+offset+2])/255
                        weight_2 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+2:entry_offset+(ver*entry_len)+offset+3])/255
                        weight_3 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+3:entry_offset+(ver*entry_len)+offset+4])/255                                                                        
                        bone_weights.append([weight_0, weight_1, weight_2, weight_3])
                    if (usage == 7):
                        index_0 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+1])
                        index_1 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+1:entry_offset+(ver*entry_len)+offset+2])
                        index_2 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+2:entry_offset+(ver*entry_len)+offset+3])
                        index_3 = read_ubyte(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+3:entry_offset+(ver*entry_len)+offset+4])
                        bone_indices.append([index_0,index_1,index_2,index_3])
                    if (usage == 8):
                        if (type == 2):
                            u = read_float(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+4])
                            v = read_float(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+4:entry_offset+(ver*entry_len)+offset+8])                                                                             
                        else:
                            u = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+2])
                            v = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+2:entry_offset+(ver*entry_len)+offset+4])                                                    
                        uv0.append([u,v*-1])
                        #print('{0} {1}'.format(u, v))
                    if (usage == 9):
                        u = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+2])
                        v = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+2:entry_offset+(ver*entry_len)+offset+4])                        
                        uv1.append([u,v*-1])
                    if (usage == 10):
                        u = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+2])
                        v = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+2:entry_offset+(ver*entry_len)+offset+4])                        
                        uv2.append([u,v*-1])
                    if (usage == 11):
                        u = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset:entry_offset+(ver*entry_len)+offset+2])
                        v = read_half(vertex_buffer[chunk][entry_offset+(ver*entry_len)+offset+2:entry_offset+(ver*entry_len)+offset+4])                        
                        uv3.append([u,v*-1])                                                
            vertex_format_start += entry_count  
        scene = bpy.context.scene
        for obj_old in bpy.data.objects:
            obj_old.select = False
        scene.objects.active = None
        group_name = strings[0][0][mesh_group_definitions[mesh_group_assignments[mesh_group_index][0]][0]]
        mesh = bpy.data.meshes.new("{1}_{0}".format(str(i).zfill(4), group_name))
        obj = bpy.data.objects.new("{1}_{0}".format(str(i).zfill(4), group_name), mesh)
        scene.objects.link(obj)
        scene.objects.active = obj
        obj.select = True
        material_to_choose = read_string(strings[0][0][material_instance[mesh_information[i][2]][0]])
        obj.data.materials.append(bpy.data.materials[material_to_choose])
        #assign to group
        print('Active are: {0}'.format(scene.objects.active))
        print('The object is: {0}'.format(bpy.ops.object))
        bpy.ops.object.group_link(group="{0}".format(group_name))
        mesh_group_obj_count = mesh_group_obj_count-1
        if (mesh_group_obj_count == 0):
            if (len(mesh_group_assignments) != mesh_group_index+1):
                mesh_group_index = mesh_group_index+1
                mesh_group_obj_count = mesh_group_assignments[mesh_group_index][1]  
        #create mesh
        mesh = bpy.context.object.data
        bm = bmesh.new()
        bverts = []
        for v in vertices:
            bverts.append(bm.verts.new(v))
        bm.verts.index_update()
        for f in faces:
            #print(f)
            try:
                bm.faces.new((bverts[f[0]], bverts[f[1]], bverts[f[2]]))
            except:
                continue
        if (len(uv0) != 0):
            uv_layer = bm.loops.layers.uv.new()
            for f in bm.faces:
                for vert, loop in zip(f.verts, f.loops):
                    #print('Vert Index: {0}, UV0VertIndex: {1}'.format(vert.index, uv0[vert.index]))
                    loop[uv_layer].uv = uv0[vert.index]
                    #print(loop[uv_layer].uv)
        if (len(uv1) != 0):
            uv_layer = bm.loops.layers.uv.new()
            for f in bm.faces:
                for vert, loop in zip(f.verts, f.loops):
                    #print('Vert Index: {0}, UV1VertIndex: {1}'.format(vert.index, uv1[vert.index]))
                    loop[uv_layer].uv = uv1[vert.index]
        if (len(uv2) != 0):
            uv_layer = bm.loops.layers.uv.new()
            for f in bm.faces:
                for vert, loop in zip(f.verts, f.loops):
                    #print('Vert Index: {0}, UV2VertIndex: {1}'.format(vert.index, uv2[vert.index]))
                    loop[uv_layer].uv = uv2[vert.index]
        if (len(uv3) != 0):
            uv_layer = bm.loops.layers.uv.new()
            for f in bm.faces:
                for vert, loop in zip(f.verts, f.loops):
                    #print('Vert Index: {0}, UV3VertIndex: {1}'.format(vert.index, uv3[vert.index]))
                    loop[uv_layer].uv = uv3[vert.index]
        bm.to_mesh(mesh)
        bm.free()
        #add bone groups
        if (len(bone_group_definitions) > 0):
            bone_grp_id = mesh_information[i][3]
            bone_grp = bone_group_definitions[bone_grp_id]
            for bn in bone_grp[2]:
                title = strings[0][0][bone_definitions[bn][0]]
                obj.vertex_groups.new(title)
            for vert in range(0, len(vertices)):
                obj.vertex_groups[bone_indices[vert][0]].add([vert], bone_weights[vert][0],'ADD') 
                obj.vertex_groups[bone_indices[vert][1]].add([vert], bone_weights[vert][1],'ADD')
                obj.vertex_groups[bone_indices[vert][2]].add([vert], bone_weights[vert][2],'ADD')
                obj.vertex_groups[bone_indices[vert][3]].add([vert], bone_weights[vert][3],'ADD')
        #print(mesh_information[i][0])
        #rotate object for blender
        bpy.ops.object.shade_smooth()
        obj.rotation_euler = (radians(90), 0, 0)
        obj.select = False
        scene.objects.active = None
    
    #print('Version: {0}'.format(round(version,2)))
    #print('Bone Definitions: {0}'.format(bone_definitions))
    print('Mesh Group Definitions: {0}'.format(mesh_group_definitions))
    print('Mesh Group Assignments: {0}'.format(mesh_group_assignments))
    print('Mesh Information: {0}'.format(mesh_information))
    print('Material Instance: {0}'.format(material_instance))
    #print('Bone Group Definitions: {0}'.format(bone_group_definitions))
    print('Texture Definitions: {0}'.format(texture_definitions))
    print('Texture Type Assignments: {0}'.format(texture_type_assignments))
    print('Material Type Assignments: {0}'.format(material_type_assignments))
    print('Mesh Format Assignments: {0}'.format(mesh_format_assignments))
    print('Mesh Format Definitions: {0}'.format(mesh_format_definitions))
    print('Vertex Format Definitions: {0}'.format(vertex_format_definitions))
    #print('String Definitions: {0}'.format(string_definitions))
    #print('Bounding Box Definitions: {0}'.format(bounding_box_definitions))
    #print('Buffer Offset Definitions: {0}'.format(buffer_offset_definitions))
    #print('LOD Face Information: {0}'.format(lod_face_info))
    #print('Face Index Definitions: {0}'.format(face_index_definitions))
    #print('Unknown Block 1: {0}'.format(unknown_block_1))
    #print('Unknown Block 2: {0}'.format(unknown_block_2))
    #print('Texture Path Hash Definitions: {0}'.format(texture_path_hash_definitions))
    #print('String Hash Definitions: {0}'.format(string_hash_definitions))
    #print('Material Parameters: {0}'.format(material_parameters))
    #print('Vertex Buffer: {0}'.format(vertex_buffer))
    print('Strings: {0}'.format(strings))
    #print(bone_weights)

    return {'FINISHED'}

def check_magic(magic):
    if (magic != bytes('FMDL', 'ascii')):
        print('Not an FMDL File')
        return 0
    else:
        return 1
    
def read_bone_definitions(data):
    string_id = read_ushort(data[0x0:0x2])
    parent_id = read_ushort(data[0x2:0x4])
    boundb_id = read_ushort(data[0x4:0x6])
    unk_1 = read_ushort(data[0x6:0x8])
    local_x = read_float(data[0x10:0x14])
    local_y = read_float(data[0x14:0x18])
    local_z = read_float(data[0x18:0x1C])
    local_w = read_float(data[0x1C:0x20])
    world_x = read_float(data[0x20:0x24])
    world_y = read_float(data[0x24:0x28])
    world_z = read_float(data[0x28:0x2C])
    world_w = read_float(data[0x2C:0x30])
    return [string_id, parent_id, boundb_id, unk_1, local_x, local_y, local_z, local_w, world_x, world_y, world_z, world_w]

def read_mesh_group_definitions(data):
    string_id = read_ushort(data[0x0:0x2])
    invisibility_flag = read_ushort(data[0x2:0x4])
    parent_id = read_ushort(data[0x4:0x6])
    unk_1 = read_ushort(data[0x6:0x8])
    return [string_id, invisibility_flag, parent_id, unk_1]

def read_mesh_group_assignments(data):
    mesh_group_id = read_ushort(data[0x4:0x6])
    object_count = read_ushort(data[0x6:0x8])
    first_obj_id = read_ushort(data[0x8:0xA])
    entry_id = read_ushort(data[0xA:0xC])
    unk_1 = read_ushort(data[0x10:0x12])
    return [mesh_group_id, object_count, first_obj_id, entry_id, unk_1]

def read_mesh_information(data):
    alpha_enum = read_ubyte(data[0x0:0x1])
    shadow_enum = read_ubyte(data[0x1:0x2])
    material_id = read_ushort(data[0x4:0x6])
    bone_id = read_ushort(data[0x6:0x8])
    entry_id = read_ushort(data[0x8:0xA])
    vertex_count = read_ushort(data[0xA:0xC])
    vertex_first_id = read_uint(data[0x10:0x14])
    vertices_face_count = read_uint(data[0x14:0x18])
    face_first_id = read_uint64(data[0x18:0x20])
    return [alpha_enum, shadow_enum, material_id, bone_id, entry_id, vertex_count, vertex_first_id, vertices_face_count, face_first_id]

def read_material_instance(data):
    string_id = read_ushort(data[0x0:0x2])
    material_id = read_ushort(data[0x4:0x6])
    tex_count = read_ubyte(data[0x6:0x7])
    parameter_count = read_ubyte(data[0x7:0x8])
    first_tex_id = read_ushort(data[0x8:0xA])
    first_parameter_id = read_ushort(data[0xA:0xC])
    return [string_id, material_id, tex_count, parameter_count, first_tex_id, first_parameter_id]

def read_bone_group_definitions(data):
    unk_1 = read_ushort(data[0x0:0x2])
    count = read_ushort(data[0x2:0x4])
    bone_id = []
    for i in range(1, count+1):
        bone_id.append(read_ushort(data[0x4+((i-1)*0x2):0x6+((i-1)*0x2)]))
    return [unk_1, count, bone_id]

def read_texture_definitions(data):
    string_id = read_ushort(data[0x0:0x2])
    path_id = read_ushort(data[0x2:0x4])
    return [string_id, path_id]

def read_texture_type_assignments(data):
    string_id = read_ushort(data[0x0:0x2])
    reference_id = read_ushort(data[0x2:0x4])
    return [string_id, reference_id]

def read_material_type_assignments(data):
    string_id = read_ushort(data[0x0:0x2])
    type_id = read_ushort(data[0x2:0x4])
    return [string_id, type_id]

def read_mesh_format_assignments(data):
    mesh_format_entries_count = read_ubyte(data[0x0:0x1])
    vertex_format_entries_count = read_ubyte(data[0x1:0x2])
    unk_1 = read_ushort(data[0x2:0x4])
    first_mesh_format_id = read_ushort(data[0x4:0x6])
    first_vertex_format_id = read_ushort(data[0x6:0x8])
    return [mesh_format_entries_count, vertex_format_entries_count, unk_1, first_mesh_format_id, first_vertex_format_id]

def read_mesh_format_definitions(data):
    buffer_offset_id = read_ubyte(data[0x0:0x1])
    vertex_format_entry_count = read_ubyte(data[0x1:0x2])
    length = read_ubyte(data[0x2:0x3])
    type = read_ubyte(data[0x3:0x4])
    offset = read_uint(data[0x4:0x8])
    return [buffer_offset_id, vertex_format_entry_count, length, type, offset]

def read_vertex_format_definitions(data):
    usage = read_ubyte(data[0x0:0x1])
    data_type = read_ubyte(data[0x1:0x2])
    offset = read_ushort(data[0x2:0x4])
    return [usage, data_type, offset]

def read_string_definitions(data):
    block_id = read_ushort(data[0x0:0x2])
    length = read_ushort(data[0x2:0x4])
    offset = read_uint(data[0x4:0x8])
    return [block_id, length, offset]
    
def read_bounding_box_definitions(data):
    max_x = read_float(data[0x0:0x4])
    max_y = read_float(data[0x4:0x8])
    max_z = read_float(data[0x8:0xC])
    max_w = read_float(data[0xC:0x10])
    min_x = read_float(data[0x10:0x14])
    min_y = read_float(data[0x14:0x18])
    min_z = read_float(data[0x18:0x1C])
    min_w = read_float(data[0x1C:0x20])
    return [max_x, max_y, max_z, max_w, min_x, min_y, min_z, min_w]

def read_buffer_offset_definitions(data):
    eof = read_uint(data[0x0:0x4])
    length = read_uint(data[0x4:0x8])
    offset = read_uint(data[0x8:0xC])
    return [eof, length, offset]

def read_lod_face_info(data):
    lod_count = read_uint(data[0x0:0x4])
    unk_1 = read_float(data[0x4:0x8])
    unk_2 = read_float(data[0x8:0xC])
    unk_3 = read_float(data[0xC:0x10])
    return [lod_count, unk_1, unk_2, unk_3]

def read_face_index_definitions(data):
    first_face_vertex = read_uint(data[0x0:0x4])
    face_vertex_count = read_uint(data[0x4:0x8])
    return [first_face_vertex, face_vertex_count]

def read_unknown_block_1(data):
    unk_1 = read_uint64(data[0x0:0x8])
    return [unk_1]

def read_unknown_block_2(data):
    unk_1 = read_float(data[0x4:0x8])
    unk_2 = read_float(data[0x8:0xC])
    unk_3 = read_float(data[0xC:0x10])
    unk_4 = read_float(data[0x10:0x14])
    unk_5 = read_uint(data[0x1C:0x20])
    unk_6 = read_uint(data[0x20:0x24])
    return [unk_1, unk_2, unk_3, unk_4, unk_5, unk_6]

def read_texture_path_hash_definitions(data):
    return [data]

def read_string_hash_definitions(data):
    return [data]

def read_material_parameters(data):
    par_1 = read_float(data[0x0:0x4])
    par_2 = read_float(data[0x4:0x8])
    par_3 = read_float(data[0x8:0xC])
    par_4 = read_float(data[0xC:0x10])
    return [par_1, par_2, par_3, par_4]

def read_vertex_buffer(data, bod):
    vertex_buffer = []
    for i in range(1, len(bod)+1):
        vertex_buffer.append(data[bod[i-1][2]:bod[i-1][2]+bod[i-1][1]])
    return vertex_buffer

def read_strings(data, sd):
    strings = []
    for i in range(1, len(sd)+1):
        strings.append(read_string((data[sd[i-1][2]:sd[i-1][2]+sd[i-1][1]]).decode()))
    return [strings]
    
def read_float(data):
    return struct.unpack('@f',data)[0]
def read_half(data):
    h = struct.unpack('@H', data)[0]
    fcomp = Float16Compressor()
    temp = fcomp.decompress(h)
    str = struct.pack('I', temp)
    valuenew = struct.unpack('f',str)[0]
    #print(valuenew)
    return valuenew
def read_uint(data):
    return struct.unpack('@I',data)[0]
def read_uint64(data):
    return struct.unpack('@Q',data)[0]
def read_ushort(data):
    return struct.unpack('@H',data)[0]
def read_ubyte(data):
    return struct.unpack('@B',data)[0]
def read_string(data):
    return str(data)

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportFMDL(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import FMDL Model"

    # ImportHelper mixin class uses this
    filename_ext = ".fmdl"

    filter_glob = StringProperty(
            default="*.fmdl",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    #use_setting = BoolProperty(
    #        name="Example Boolean",
    #        description="Example Tooltip",
    #        default=True,
    #        )
    use_setting = ()

    #type = EnumProperty(
    #        name="Example Enum",
    #        description="Choose between two items",
    #        items=(('OPT_A', "First Option", "Description one"),
    #               ('OPT_B', "Second Option", "Description two")),
    #        default='OPT_A',
    #        )
    type = EnumProperty()

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting, self)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportFMDL.bl_idname, text="FMDL Import Operator")


def register():
    bpy.utils.register_class(ImportFMDL)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportFMDL)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')

class Float16Compressor:
	def __init__(self):
		self.temp = 0
		
	def compress(self,float32):
		F16_EXPONENT_BITS = 0x1F
		F16_EXPONENT_SHIFT = 10
		F16_EXPONENT_BIAS = 15
		F16_MANTISSA_BITS = 0x3ff
		F16_MANTISSA_SHIFT =  (23 - F16_EXPONENT_SHIFT)
		F16_MAX_EXPONENT =  (F16_EXPONENT_BITS << F16_EXPONENT_SHIFT)

		a = struct.pack('>f',float32)
		b = binascii.hexlify(a)

		f32 = int(b,16)
		f16 = 0
		sign = (f32 >> 16) & 0x8000
		exponent = ((f32 >> 23) & 0xff) - 127
		mantissa = f32 & 0x007fffff
				
		if exponent == 128:
			f16 = sign | F16_MAX_EXPONENT
			if mantissa:
				f16 |= (mantissa & F16_MANTISSA_BITS)
		elif exponent > 15:
			f16 = sign | F16_MAX_EXPONENT
		elif exponent > -15:
			exponent += F16_EXPONENT_BIAS
			mantissa >>= F16_MANTISSA_SHIFT
			f16 = sign | exponent << F16_EXPONENT_SHIFT | mantissa
		else:
			f16 = sign
		return f16
		
	def decompress(self,float16):
		s = int((float16 >> 15) & 0x00000001)    # sign
		e = int((float16 >> 10) & 0x0000001f)    # exponent
		f = int(float16 & 0x000003ff)            # fraction

		if e == 0:
			if f == 0:
				return int(s << 31)
			else:
				while not (f & 0x00000400):
					f = f << 1
					e -= 1
				e += 1
				f &= ~0x00000400
				#print(s,e,f)
		elif e == 31:
			if f == 0:
				return int((s << 31) | 0x7f800000)
			else:
				return int((s << 31) | 0x7f800000 | (f << 13))

		e = e + (127 -15)
		f = f << 13
		return int((s << 31) | (e << 23) | f)

#----------------------------------------------------------
# File popup.py
# from API documentation
#----------------------------------------------------------
 
#import bpy
#from bpy.props import *
# 
#theString = "Lorem ..."
# 
#class DialogOperator(bpy.types.Operator):
#    bl_idname = "object.dialog_operator"
#    bl_label = "Simple Dialog Operator"
# 
#    my_string = StringProperty(name="String Value")
# 
#    def execute(self, context):
#        message = "'%s'" % (self.my_string)
#        self.report({'INFO'}, message)
#        print(message)
#        return {'FINISHED'}
# 
#    def invoke(self, context, event):
#        global theString
#        self.my_string = theString
#        return context.window_manager.invoke_props_dialog(self)
# 
# 
#bpy.utils.register_class(DialogOperator)
# 
## Invoke the dialog when loading
#bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
# 
##
##    Panel in tools region
##
#class DialogPanel(bpy.types.Panel):
#    bl_label = "Dialog"
#    bl_space_type = "VIEW_3D"
#    bl_region_type = "UI"
# 
#    def draw(self, context):
#        global theString
#        theString = "Code snippets"
#        self.layout.operator("object.dialog_operator")
# 
##
##	Registration
#bpy.utils.register_module(__name__)