from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Allow read for everyone, write only for owner"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        # Check if obj has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsWorkerOwner(BasePermission):
    """Allow only the worker profile owner to modify"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsBookingParticipant(BasePermission):
    """Allow only booking participants (client or worker) to access"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Client can access their own bookings
        if obj.client == user:
            return True
        
        # Worker can access bookings assigned to them
        if hasattr(user, 'worker_profile') and obj.worker == user.worker_profile:
            return True
        
        return False


class IsMessageParticipant(BasePermission):
    """Allow only message sender or receiver to access"""
    
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user or obj.receiver == request.user
