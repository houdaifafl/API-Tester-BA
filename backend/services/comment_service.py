from datetime import datetime
from models.base import db
from models.comment_model import Comment
from models.workspace_model import Workspace
from models.workspace_member_model import WorkspaceMember
from models.request_model import Request

def _get_active_member_ids(workspace):
    active_ids = {workspace.user_id}
    for membership in workspace.memberships:
        active_ids.add(membership.user_id)
    return active_ids

def _serialize_single_comment(comment, active_ids, owner_id):
    creator = comment.user
    if comment.user_id == owner_id or comment.user_id in active_ids:
        username = creator.username if creator else "Unknown User"
    else:
        username = "Deactivated User"

    return {
        'id': comment.id,
        'workspace_id': comment.workspace_id,
        'user_id': comment.user_id,
        'username': username,
        'content': comment.content,
        'parent_id': comment.parent_id,
        'request_id': comment.request_id,
        'request_name': comment.request.name if comment.request else None,
        'target_tab': comment.target_tab,
        'target_key': comment.target_key,
        'created_at': comment.created_at.isoformat() + 'Z',
        'updated_at': comment.updated_at.isoformat() + 'Z'
    }

def get_comments(workspace_id, user_id, request_id=None):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, "Workspace not found"

    # Verify membership/ownership
    is_owner = (workspace.user_id == user_id)
    is_member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first() is not None
    if not is_owner and not is_member:
        return None, "Forbidden"

    active_ids = _get_active_member_ids(workspace)

    # Query parent comments
    query = Comment.query.filter_by(workspace_id=workspace_id, parent_id=None)
    if request_id is not None:
        query = query.filter_by(request_id=request_id)

    # Order parent comments chronologically
    parent_comments = query.order_by(Comment.created_at.asc()).all()

    serialized = []
    for parent in parent_comments:
        p_dict = _serialize_single_comment(parent, active_ids, workspace.user_id)
        # Order replies chronologically
        replies = Comment.query.filter_by(parent_id=parent.id).order_by(Comment.created_at.asc()).all()
        p_dict['replies'] = [_serialize_single_comment(r, active_ids, workspace.user_id) for r in replies]
        serialized.append(p_dict)

    return serialized, None

def create_comment(workspace_id, user_id, content, parent_id=None, request_id=None, target_tab=None, target_key=None):
    if not content or not content.strip():
        return None, "Content is required"

    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, "Workspace not found"

    # Verify membership/ownership
    is_owner = (workspace.user_id == user_id)
    is_member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first() is not None
    if not is_owner and not is_member:
        return None, "Forbidden"

    # Validate parent comment (single-level nesting restriction)
    if parent_id is not None:
        parent = db.session.get(Comment, parent_id)
        if not parent:
            return None, "Parent comment not found"
        if parent.workspace_id != workspace_id:
            return None, "Parent comment workspace mismatch"
        if parent.parent_id is not None:
            return None, "Nested child comments are not allowed (single-level only)"

    # Validate request association
    if request_id is not None:
        req = db.session.get(Request, request_id)
        if not req:
            return None, "Request not found"
        # Verify request collection belongs to this workspace
        if req.collection.workspace_id != workspace_id:
            return None, "Request workspace mismatch"

    # Validate target tab values
    if target_tab is not None and target_tab not in {'params', 'headers', 'body', 'auth', 'collection'}:
        return None, "Invalid target tab"

    new_comment = Comment(
        workspace_id=workspace_id,
        user_id=user_id,
        content=content.strip(),
        parent_id=parent_id,
        request_id=request_id,
        target_tab=target_tab,
        target_key=target_key
    )
    db.session.add(new_comment)
    db.session.commit()

    active_ids = _get_active_member_ids(workspace)
    serialized = _serialize_single_comment(new_comment, active_ids, workspace.user_id)
    if parent_id is None:
        serialized['replies'] = []

    return serialized, None

def edit_comment(comment_id, user_id, content):
    if not content or not content.strip():
        return None, "Content is required"

    comment = db.session.get(Comment, comment_id)
    if not comment:
        return None, "Comment not found"

    # Only creator can edit comment
    if comment.user_id != user_id:
        return None, "Forbidden"

    workspace = db.session.get(Workspace, comment.workspace_id)
    # Check if user is still workspace member/owner
    is_owner = (workspace.user_id == user_id)
    is_member = WorkspaceMember.query.filter_by(workspace_id=comment.workspace_id, user_id=user_id).first() is not None
    if not is_owner and not is_member:
        return None, "Forbidden"

    comment.content = content.strip()
    comment.updated_at = datetime.utcnow()
    db.session.commit()

    active_ids = _get_active_member_ids(workspace)
    serialized = _serialize_single_comment(comment, active_ids, workspace.user_id)
    if comment.parent_id is None:
        replies = Comment.query.filter_by(parent_id=comment.id).order_by(Comment.created_at.asc()).all()
        serialized['replies'] = [_serialize_single_comment(r, active_ids, workspace.user_id) for r in replies]

    return serialized, None

def delete_comment(comment_id, user_id):
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return None, "Comment not found"

    workspace = db.session.get(Workspace, comment.workspace_id)

    # Allowed if:
    # 1. User is the creator of the comment
    # 2. User is the workspace owner (deleting other's comments)
    is_owner = (workspace.user_id == user_id)
    is_creator = (comment.user_id == user_id)

    if not is_creator and not is_owner:
        return None, "Forbidden"

    # Check if user is still a member or owner of the workspace
    is_member = WorkspaceMember.query.filter_by(workspace_id=comment.workspace_id, user_id=user_id).first() is not None
    if not is_owner and not is_member:
        return None, "Forbidden"

    db.session.delete(comment)
    db.session.commit()
    return True, None
