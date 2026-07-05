from models.base import db
from models.invitation_model import Invitation
from models.workspace_member_model import WorkspaceMember
from models.workspace_model import Workspace
from models.user_model import User

def create_invitation(workspace_id, inviter_id, invitee_username, role='viewer'):
    # Verify workspace exists
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'workspace_not_found'

    # Verify inviter is owner of workspace (Editors/Viewers cannot invite)
    is_owner = (workspace.user_id == inviter_id)
    if not is_owner:
        return None, 'forbidden'

    # Validate role
    if role not in ['editor', 'viewer']:
        return None, 'invalid_role'

    # Check if invitee exists
    invitee = User.query.filter_by(username=invitee_username).first()
    if not invitee:
        return None, 'user_not_found'

    # Check if invitee is already a member (owner or member)
    is_invitee_owner = (workspace.user_id == invitee.id)
    invitee_member_record = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=invitee.id).first()
    is_invitee_member = invitee_member_record is not None
    
    if is_invitee_owner or is_invitee_member:
        return None, 'already_member'

    # Check if a pending invitation already exists to this invitee for this workspace
    existing_invitation = Invitation.query.filter_by(
        workspace_id=workspace_id,
        invitee_id=invitee.id,
        status='pending'
    ).first()
    if existing_invitation:
        return None, 'invitation_pending'

    # Insert Invitation row
    invitation = Invitation(
        workspace_id=workspace_id,
        inviter_id=inviter_id,
        invitee_id=invitee.id,
        status='pending',
        role=role
    )
    db.session.add(invitation)
    db.session.commit()
    return {'id': invitation.id}, None

def get_pending_invitations(user_id):
    invitations = Invitation.query.filter_by(invitee_id=user_id, status='pending').all()
    serialized = []
    for inv in invitations:
        workspace_name = inv.workspace.name if inv.workspace else "Unknown Workspace"
        inviter_username = inv.inviter.username if inv.inviter else "Unknown User"
        inviter_email = inv.inviter.email if inv.inviter else "Unknown Email"
        serialized.append({
            'id': inv.id,
            'workspace_id': inv.workspace_id,
            'workspace_name': workspace_name,
            'inviter_username': inviter_username,
            'inviter_email': inviter_email,
            'status': inv.status,
            'role': inv.role or 'viewer'
        })
    return serialized, None

def accept_invitation(invitation_id, user_id):
    invitation = db.session.get(Invitation, invitation_id)
    if not invitation:
        return None, 'not_found'
        
    if invitation.invitee_id != user_id:
        return None, 'forbidden'
        
    if invitation.status != 'pending':
        return None, 'not_pending'
        
    invitation.status = 'accepted'
    
    # Create WorkspaceMember entry
    existing = WorkspaceMember.query.filter_by(workspace_id=invitation.workspace_id, user_id=user_id).first()
    if not existing:
        member = WorkspaceMember(workspace_id=invitation.workspace_id, user_id=user_id, role=invitation.role or 'viewer')
        db.session.add(member)
        
    db.session.commit()
    return True, None

def decline_invitation(invitation_id, user_id):
    invitation = db.session.get(Invitation, invitation_id)
    if not invitation:
        return None, 'not_found'
        
    if invitation.invitee_id != user_id:
        return None, 'forbidden'
        
    if invitation.status != 'pending':
        return None, 'not_pending'
        
    invitation.status = 'declined'
    db.session.commit()
    return True, None
