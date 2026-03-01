# Auto Bone Connector

A Blender addon for streamlined bone rigging with intelligent connection tools, follow-through constraints, and collision support.

## Features

### Edit Mode Tools
- **Connect to Active** — Parent multiple bones to the active bone with flexible options:
  - *Keep Offset*: Parent while preserving current positions
  - *Connected*: Snap child heads to parent tail
  - *Tail to Head*: Move parent tail to child head
- **Auto Connect by Distance** — Automatically parent bones to the nearest neighbor within a threshold
- **Toggle Connect/Offset** — Quickly switch parented bones between Connected and Keep Offset modes
- **Disconnect Tools** — Disconnect bones or completely clear parenting

### Pose Mode Tools
- **Auto Damp Track Chain** — Add Damped Track constraints for automatic follow-through animation:
  - Gradient influence from root to tip
  - track immediate child 
  - Configurable influence values and track axis
- **Performance Controls** — Toggle constraints on/off to speed up viewport playback

## Installation

1. Download the latest release python file
2. In Blender, go to **Edit > Preferences > Add-ons > Install...**
3. Select the downloaded python file
4. Enable the addon by checking the checkbox

## Requirements

- Blender 3.0 or newer

## Usage

Access all tools in the 3D Viewport sidebar (**N** panel) under the **Bone Tools** tab.

### Edit Mode Workflow

#### Connect to Active
1. Select multiple bones in Edit Mode
2. Make the desired parent bone active (last selected)
3. Choose your connection method:
   - Click **Keep Offset** to parent without moving
   - Click **Connected** to snap bones together
   - Click **Tail to Head** to move parent tail to child


#### Auto Connect by Distance
1. Select multiple bones in Edit Mode
2. Click **Auto by Distance**
3. Bones will automatically parent to their nearest neighbor within the threshold

#### Toggle Between Modes
1. Select already-parented bones
2. Click **Toggle Connect/Offset**
3. Connected bones switch to Keep Offset, and vice versa

**Demo:**



https://github.com/user-attachments/assets/c952246e-88c3-437f-be11-dc90c5a7f731




#### Disconnect/Clear Parent
- **Disconnect Only**: Keep parent but disconnect physical connection
- **Clear Parent All**: Completely remove parent relationship

### Pose Mode Workflow

#### Follow-Through Animation
1. Select all bones in a chain (in Pose Mode)
2. Adjust the settings in the panel:
   - **Mode**: Choose "Immediate Child" for chain hierarchy or "Chain Tip" for aiming at the end
   - **Root Influence**: Set how strongly the root follows (0 = rigid, 1 = full follow)
   - **Tip Influence**: Set how strongly the tip follows (0 = rigid, 1 = full follow)
   - **Axis**: Which bone axis points toward the target
3. Click **Add Damp Track Chain**

**Demo:**



https://github.com/user-attachments/assets/4739c2f6-7f89-4845-9682-ee7964ca8e74




4. Use **Toggle Damp Track** to temporarily disable for better playback performance
5. Use **Remove Damp Track** to delete all Damped Track constraints

#### Performance Optimization
- **Disable All**: Mute all constraints for maximum viewport performance
- **Enable All**: Re-enable all constraints for animation playback

## Tips

- **Performance**: Use "Disable All (Fast)" when animating complex rigs, then "Enable All (Normal)" for final review
- **Naming**: Bones are sorted alphabetically for chain operations — consistent naming helps predictable results
- **Influence Curves**: Set root influence low (0.1) and tip high (1.0) for natural follow-through on tails, hair, or cables
- **Auto Connect**: The threshold controls how far apart bones can be to still connect — increase for looser connections

## Changelog

### v1.0.1
- Added **Toggle Connect/Offset** for quick mode switching
- Added **Clear Parent All** for complete unparenting
- Fixed damp track to handle branching chains
- Improved auto-connect distance algorithm
- Removed collision functions (not working properly)
- Removed chain operations and spline IK


## Author

**Garuh143**

---
This is a free hobby project.
Contributions and feedback welcome!
