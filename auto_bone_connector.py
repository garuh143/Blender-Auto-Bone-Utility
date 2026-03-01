bl_info = {
    "name": "Auto Bone Connector",
    "author": "Garuh143",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Bone Tools",
    "description": "Auto-connect bones with keep offset option",
    "category": "Rigging",
}

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from bpy.types import Panel, Operator


class BONE_OT_connect_to_active(Operator):
    """Connect selected bones to active bone with options"""
    bl_idname = "bone.connect_to_active"
    bl_label = "Connect to Active"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="Mode",
        description="How to connect bones",
        items=[
            ('KEEP_OFFSET', "Keep Offset", "Parent but keep current position"),
            ('CONNECTED', "Connected", "Snap child head to parent tail"),
            ('TAIL_TO_HEAD', "Tail to Head", "Move parent tail to child head"),
        ],
        default='KEEP_OFFSET'
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_ARMATURE':
            return False
        if context.active_bone is None:
            return False
        if len(context.selected_bones) < 2:
            return False
        return True

    def execute(self, context):
        active_bone = context.active_bone
        selected_bones = context.selected_bones.copy()
        child_bones = [b for b in selected_bones if b != active_bone]

        for child_bone in child_bones:
            child_bone.parent = active_bone

            if self.mode == 'KEEP_OFFSET':
                child_bone.use_connect = False
            elif self.mode == 'CONNECTED':
                child_bone.use_connect = True
            elif self.mode == 'TAIL_TO_HEAD':
                active_bone.tail = child_bone.head
                child_bone.use_connect = True

        self.report({'INFO'}, "Connected %d bone(s) - %s" % (len(child_bones), self.mode))
        return {'FINISHED'}


class BONE_OT_connect_chain(Operator):
    """Connect bones in a chain (each bone parents to previous)"""
    bl_idname = "bone.connect_chain"
    bl_label = "Connect Chain"
    bl_options = {'REGISTER', 'UNDO'}

    keep_offset: BoolProperty(
        name="Keep Offset",
        description="Keep current positions instead of snapping",
        default=True
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_ARMATURE':
            return False
        if len(context.selected_bones) < 2:
            return False
        return True

    def execute(self, context):
        bones = list(context.selected_bones)
        bones.sort(key=lambda b: b.name)

        for i in range(1, len(bones)):
            child = bones[i]
            parent = bones[i - 1]
            child.parent = parent
            child.use_connect = not self.keep_offset

        mode_str = "keep offset" if self.keep_offset else "connected"
        self.report({'INFO'}, "Chained %d bones (%s)" % (len(bones), mode_str))
        return {'FINISHED'}


class BONE_OT_disconnect_bones(Operator):
    """Disconnect selected bones from their parents"""
    bl_idname = "bone.disconnect_bones"
    bl_label = "Disconnect Bones"
    bl_options = {'REGISTER', 'UNDO'}

    clear_parent: BoolProperty(
        name="Clear Parent",
        description="Also clear parent relationship",
        default=False
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_ARMATURE':
            return False
        if len(context.selected_bones) == 0:
            return False
        return True

    def execute(self, context):
        count = 0
        for bone in context.selected_bones:
            if bone.parent is not None:
                bone.use_connect = False
                if self.clear_parent:
                    bone.parent = None
                count += 1

        action = "Unparented" if self.clear_parent else "Disconnected"
        self.report({'INFO'}, "%s %d bone(s)" % (action, count))
        return {'FINISHED'}


class BONE_OT_connect_by_distance(Operator):
    """Auto-connect bones to nearest parent within threshold"""
    bl_idname = "bone.connect_by_distance"
    bl_label = "Auto Connect by Distance"
    bl_options = {'REGISTER', 'UNDO'}

    threshold: FloatProperty(
        name="Distance Threshold",
        description="Maximum distance to consider for parenting",
        default=0.1,
        min=0.001,
        soft_max=1000.0,
        unit='LENGTH'
    )

    use_connect: BoolProperty(
        name="Connected",
        description="Snap child head to parent tail (disable for keep offset)",
        default=False
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_ARMATURE':
            return False
        if len(context.selected_bones) < 2:
            return False
        return True

    def execute(self, context):
        bones = list(context.selected_bones)
        connected_count = 0

        for child in bones:
            nearest_parent = None
            nearest_dist = self.threshold

            for potential_parent in bones:
                if potential_parent == child:
                    continue

                dist = (child.head - potential_parent.tail).length

                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_parent = potential_parent

            if nearest_parent:
                child.parent = nearest_parent
                child.use_connect = self.use_connect
                connected_count += 1

        mode_str = "connected" if self.use_connect else "keep offset"
        self.report({'INFO'}, "Parented %d bones (%s)" % (connected_count, mode_str))
        return {'FINISHED'}


class BONE_OT_auto_damp_track(Operator):
    """Add Damped Track constraints to each bone pointing to its child with gradient influence"""
    bl_idname = "bone.auto_damp_track"
    bl_label = "Auto Damp Track Chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        if len(context.selected_pose_bones) < 2:
            return False
        return True

    def execute(self, context):
        selected_bones = list(context.selected_pose_bones)
        scene = context.scene

        # Get settings from scene
        target_mode = scene.damp_track_target_mode
        root_influence = scene.damp_track_root_influence
        tip_influence = scene.damp_track_tip_influence
        track_axis = scene.damp_track_axis

        # Find all root bones (no parent in the selection)
        roots = []
        for bone in selected_bones:
            if bone.parent not in selected_bones:
                roots.append(bone)

        # Build chains from each root
        chains = []
        for root in roots:
            chain = []
            current = root
            while current and current in selected_bones:
                chain.append(current)
                # Find child in our selection
                next_bone = None
                for b in selected_bones:
                    if b.parent == current:
                        next_bone = b
                        break
                current = next_bone
            if len(chain) >= 2:
                chains.append(chain)

        # If no valid chains found, fall back to treating all as one chain
        if not chains:
            chains = [sorted(selected_bones, key=lambda b: b.name)]

        # Add damped track constraints for each chain
        constrained_count = 0
        for chain in chains:
            # Get the tip bone (last in chain) for TIP mode
            tip_bone = chain[-1] if chain else None

            for i, pose_bone in enumerate(chain):
                # Skip tip bone - it has no child to track
                if pose_bone == tip_bone and target_mode == 'CHILD':
                    continue

                # Determine target bone
                if target_mode == 'CHILD':
                    # Find the child bone (next in chain)
                    target_bone = None
                    for b in chain:
                        if b.parent == pose_bone:
                            target_bone = b
                            break
                    if target_bone is None:
                        continue
                else:  # TIP mode
                    target_bone = tip_bone
                    if pose_bone == tip_bone:
                        continue  # Tip can't track itself

                # Calculate gradient influence (decreases toward root)
                if len(chain) > 1:
                    factor = i / (len(chain) - 1)  # 0 at root, 1 at tip
                else:
                    factor = 0.5

                # Influence: tip = tip_influence, root = root_influence
                influence = root_influence + (tip_influence - root_influence) * factor

                # Create constraint - bone tracks its target
                constraint = pose_bone.constraints.new('DAMPED_TRACK')
                constraint.target = context.active_object
                constraint.subtarget = target_bone.name
                constraint.track_axis = track_axis
                constraint.influence = influence

                # Name it nicely
                constraint.name = "Auto Damp Track"
                constrained_count += 1

        self.report({'INFO'}, "Added %d Damped Track constraints (%d chains)" % (constrained_count, len(chains)))
        return {'FINISHED'}


class BONE_OT_remove_damp_track(Operator):
    """Remove all Damped Track constraints from selected bones"""
    bl_idname = "bone.remove_damp_track"
    bl_label = "Remove Damp Track"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return len(context.selected_pose_bones) > 0

    def execute(self, context):
        count = 0
        for pose_bone in context.selected_pose_bones:
            constraints_to_remove = [c for c in pose_bone.constraints if c.type == 'DAMPED_TRACK']
            for constraint in constraints_to_remove:
                pose_bone.constraints.remove(constraint)
                count += 1

        self.report({'INFO'}, "Removed %d Damped Track constraints" % count)
        return {'FINISHED'}


class BONE_OT_toggle_damp_track(Operator):
    """Toggle Damped Track constraints on/off for better performance"""
    bl_idname = "bone.toggle_damp_track"
    bl_label = "Toggle Damp Track"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="Mode",
        description="What to do with the constraints",
        items=[
            ('HIDE', "Hide", "Temporarily disable constraints (mute them)"),
            ('SHOW', "Show", "Re-enable muted constraints"),
            ('TOGGLE', "Toggle", "Flip current state of all constraints"),
        ],
        default='TOGGLE'
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return len(context.selected_pose_bones) > 0

    def execute(self, context):
        muted_count = 0
        enabled_count = 0

        for pose_bone in context.selected_pose_bones:
            damp_constraints = [c for c in pose_bone.constraints if c.type == 'DAMPED_TRACK']

            for constraint in damp_constraints:
                if self.mode == 'HIDE':
                    constraint.mute = True
                    muted_count += 1
                elif self.mode == 'SHOW':
                    constraint.mute = False
                    enabled_count += 1
                else:  # TOGGLE
                    constraint.mute = not constraint.mute
                    if constraint.mute:
                        muted_count += 1
                    else:
                        enabled_count += 1

        if self.mode == 'HIDE':
            self.report({'INFO'}, "Muted %d constraints (animation paused)" % muted_count)
        elif self.mode == 'SHOW':
            self.report({'INFO'}, "Enabled %d constraints (animation active)" % enabled_count)
        else:
            self.report({'INFO'}, "Toggled: %d muted, %d enabled" % (muted_count, enabled_count))
        return {'FINISHED'}


class BONE_OT_disable_all_constraints(Operator):
    """Disable all constraints on selected bones for maximum performance"""
    bl_idname = "bone.disable_all_constraints"
    bl_label = "Disable All Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return len(context.selected_pose_bones) > 0

    def execute(self, context):
        muted_count = 0
        for pose_bone in context.selected_pose_bones:
            for constraint in pose_bone.constraints:
                if not constraint.mute:
                    constraint.mute = True
                    muted_count += 1

        self.report({'INFO'}, "Muted %d constraints (max performance)" % muted_count)
        return {'FINISHED'}


class BONE_OT_enable_all_constraints(Operator):
    """Re-enable all constraints on selected bones"""
    bl_idname = "bone.enable_all_constraints"
    bl_label = "Enable All Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        return len(context.selected_pose_bones) > 0

    def execute(self, context):
        enabled_count = 0
        for pose_bone in context.selected_pose_bones:
            for constraint in pose_bone.constraints:
                if constraint.mute:
                    constraint.mute = False
                    enabled_count += 1

        self.report({'INFO'}, "Enabled %d constraints (animation active)" % enabled_count)
        return {'FINISHED'}


class BONE_OT_add_collision_constraint(Operator):
    """Add Limit Distance constraint for simple collision with a target object"""
    bl_idname = "bone.add_collision_constraint"
    bl_label = "Add Bone Collision"
    bl_options = {'REGISTER', 'UNDO'}

    distance: FloatProperty(
        name="Distance",
        description="Minimum distance from collision object",
        default=0.1,
        min=0.001,
        soft_max=1.0,
        unit='LENGTH'
    )

    limit_mode: EnumProperty(
        name="Limit Mode",
        description="How to limit the distance",
        items=[
            ('LIMITDIST_OUTSIDE', "Outside", "Keep bone outside the sphere"),
            ('LIMITDIST_INSIDE', "Inside", "Keep bone inside the sphere"),
            ('LIMITDIST_ONSURFACE', "On Surface", "Keep bone on surface"),
        ],
        default='LIMITDIST_OUTSIDE'
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        if len(context.selected_pose_bones) < 1:
            return False
        # Need an active object as collision target
        if context.active_object is None:
            return False
        return True

    def execute(self, context):
        collision_target = context.active_object
        selected_bones = context.selected_pose_bones

        added_count = 0
        for pose_bone in selected_bones:
            # Skip if bone is the target itself
            if pose_bone.id_data == collision_target:
                continue

            constraint = pose_bone.constraints.new('LIMIT_DISTANCE')
            constraint.target = collision_target
            constraint.distance = self.distance
            constraint.limit_mode = self.limit_mode
            constraint.use_transform_limit = True
            constraint.name = "Collision Limit"
            added_count += 1

        self.report({'INFO'}, "Added %d collision constraints targeting '%s'" % (added_count, collision_target.name))
        return {'FINISHED'}


class BONE_OT_setup_spline_ik_hair(Operator):
    """Setup Spline IK with Soft Body for hair collision (select curve then bones)"""
    bl_idname = "bone.setup_spline_ik_hair"
    bl_label = "Setup Spline IK Hair"
    bl_options = {'REGISTER', 'UNDO'}

    chain_count: bpy.props.IntProperty(
        name="Chain Length",
        description="Number of bones in the spline IK chain",
        default=4,
        min=2,
        max=64
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'POSE':
            return False
        # Need a curve selected as active object
        if context.active_object is None:
            return False
        if context.active_object.type != 'CURVE':
            return False
        if len(context.selected_pose_bones) < 1:
            return False
        return True

    def execute(self, context):
        curve_obj = context.active_object
        selected_bones = list(context.selected_pose_bones)

        # Sort bones to find the root of the chain
        selected_bones.sort(key=lambda b: b.name)
        root_bone = selected_bones[0]

        # Add Spline IK constraint to root bone
        constraint = root_bone.constraints.new('SPLINE_IK')
        constraint.target = curve_obj
        constraint.chain_count = min(self.chain_count, len(selected_bones))
        constraint.use_chain_offset = True
        constraint.use_y_stretch = True
        constraint.use_curve_radius = True
        constraint.name = "Spline IK Hair"

        self.report({'INFO'}, "Added Spline IK to '%s' targeting curve '%s'" % (root_bone.name, curve_obj.name))
        self.report({'INFO'}, "Add Soft Body to the curve for collision physics!")
        return {'FINISHED'}


class BONE_PT_auto_connector_panel(Panel):
    """Auto Bone Connector Panel"""
    bl_label = "Auto Bone Connector"
    bl_idname = "BONE_PT_auto_connector"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone Tools'

    def draw(self, context):
        layout = self.layout

        if context.mode == 'EDIT_ARMATURE':
            box1 = layout.box()
            box1.label(text="Connect to Active:", icon='BONE_DATA')
            col1 = box1.column(align=True)
            col1.operator("bone.connect_to_active", text="Keep Offset").mode = 'KEEP_OFFSET'
            col1.operator("bone.connect_to_active", text="Connected").mode = 'CONNECTED'
            col1.operator("bone.connect_to_active", text="Tail to Head").mode = 'TAIL_TO_HEAD'

            layout.separator()

            box2 = layout.box()
            box2.label(text="Chain Operations:", icon='CONSTRAINT_BONE')
            col2 = box2.column(align=True)
            col2.operator("bone.connect_chain", text="Chain (Keep Offset)").keep_offset = True
            col2.operator("bone.connect_chain", text="Chain (Connected)").keep_offset = False

            layout.separator()

            box3 = layout.box()
            box3.label(text="Auto Connect:", icon='MODIFIER')
            col3 = box3.column(align=True)
            col3.operator("bone.connect_by_distance", text="Auto by Distance")

            layout.separator()

            box4 = layout.box()
            box4.label(text="Disconnect:", icon='X')
            col4 = box4.column(align=True)
            col4.operator("bone.disconnect_bones", text="Disconnect Only").clear_parent = False
            col4.operator("bone.disconnect_bones", text="Clear Parent").clear_parent = True

        elif context.mode == 'POSE':
            box = layout.box()
            box.label(text="Follow-Through:", icon='CONSTRAINT')
            col = box.column(align=True)
            col.label(text="Select all bones in chain(s)")
            col.separator()

            # Settings in panel
            col.prop(context.scene, "damp_track_target_mode", text="Mode")
            col.prop(context.scene, "damp_track_root_influence", text="Root")
            col.prop(context.scene, "damp_track_tip_influence", text="Tip")
            col.prop(context.scene, "damp_track_axis", text="Axis")
            col.separator()

            col.operator("bone.auto_damp_track", text="Add Damp Track Chain")
            col.separator()
            col.operator("bone.remove_damp_track", text="Remove Damp Track", icon='X')

            layout.separator()

            # Performance section
            box2 = layout.box()
            box2.label(text="Performance:", icon='HIDE_ON')
            col2 = box2.column(align=True)
            col2.operator("bone.toggle_damp_track", text="Toggle Damp Track")
            col2.operator("bone.disable_all_constraints", text="Disable All (Fast)")
            col2.operator("bone.enable_all_constraints", text="Enable All (Normal)")

            layout.separator()

            # Collision section
            box3 = layout.box()
            box3.label(text="Collision:", icon='MOD_PHYSICS')
            col3 = box3.column(align=True)
            col3.label(text="Select obj + bones:")
            col3.operator("bone.add_collision_constraint", text="Add Collision Sphere")
            col3.separator()
            col3.label(text="Select curve + bones:")
            col3.operator("bone.setup_spline_ik_hair", text="Setup Spline IK")

        else:
            layout.label(text="Switch to Edit or Pose Mode", icon='INFO')


classes = (
    BONE_OT_connect_to_active,
    BONE_OT_connect_chain,
    BONE_OT_disconnect_bones,
    BONE_OT_connect_by_distance,
    BONE_OT_auto_damp_track,
    BONE_OT_remove_damp_track,
    BONE_OT_toggle_damp_track,
    BONE_OT_disable_all_constraints,
    BONE_OT_enable_all_constraints,
    BONE_OT_add_collision_constraint,
    BONE_OT_setup_spline_ik_hair,
    BONE_PT_auto_connector_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Scene properties for damp track settings
    bpy.types.Scene.damp_track_target_mode = EnumProperty(
        name="Target Mode",
        description="Which bone to track",
        items=[
            ('CHILD', "Immediate Child", "Each bone tracks its direct child"),
            ('TIP', "Chain Tip", "All bones track the final tip bone"),
        ],
        default='CHILD'
    )
    bpy.types.Scene.damp_track_root_influence = FloatProperty(
        name="Root Influence",
        description="Influence at root (0 = rigid, 1 = full follow)",
        default=0.1,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    bpy.types.Scene.damp_track_tip_influence = FloatProperty(
        name="Tip Influence",
        description="Influence at tip (0 = rigid, 1 = full follow)",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    bpy.types.Scene.damp_track_axis = EnumProperty(
        name="Track Axis",
        description="Axis pointing to target",
        items=[
            ('TRACK_X', "X", ""),
            ('TRACK_Y', "Y", ""),
            ('TRACK_Z', "Z", ""),
            ('TRACK_NEGATIVE_X', "-X", ""),
            ('TRACK_NEGATIVE_Y', "-Y", ""),
            ('TRACK_NEGATIVE_Z', "-Z", ""),
        ],
        default='TRACK_Y'
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.damp_track_target_mode
    del bpy.types.Scene.damp_track_root_influence
    del bpy.types.Scene.damp_track_tip_influence
    del bpy.types.Scene.damp_track_axis


if __name__ == "__main__":
    register()
