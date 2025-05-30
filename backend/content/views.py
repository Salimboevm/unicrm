from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Count

from .models import DigitalContent, ContentProgress
from .serializers import (
    DigitalContentSerializer, 
    ContentProgressSerializer,
)


class DigitalContentViewSet(viewsets.ModelViewSet):
    """ViewSet for digital content management"""
    queryset = DigitalContent.objects.all().order_by('-created_at')
    serializer_class = DigitalContentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category', 'author']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For unauthenticated users, return an empty queryset
        if not self.request.user.is_authenticated:
            return DigitalContent.objects.none()
            
        # Regular users can only see active content
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
            # Filter by access level based on user's membership
            profile = self.request.user.profile
            if profile and profile.current_membership:
                membership_type = profile.current_membership.membership_type
                if membership_type == 'community':
                    queryset = queryset.filter(
                        Q(access_level='all') | Q(access_level='community')
                    )
                elif membership_type == 'key_access':
                    queryset = queryset.filter(
                        Q(access_level='all') | Q(access_level='community') | 
                        Q(access_level='key_access')
                    )
                elif membership_type == 'creative_workspace':
                    # Creative workspace members can access all content
                    pass
            else:
                # Non-members can't access any content
                queryset = queryset.none()
                
        # Apply filter by content type
        content_type = self.request.query_params.get('content_type', None)
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
            
        # Filter by featured flag
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(featured=True)
            
        # Apply filter by access level (admin only)
        if self.request.user.is_staff:
            access_level = self.request.query_params.get('access_level', None)
            if access_level:
                queryset = queryset.filter(access_level=access_level)
                
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_content(self, request):
        """Get all content the current user has interacted with"""
        user = request.user
        content_ids = ContentProgress.objects.filter(user=user).values_list('content_id', flat=True)
        queryset = self.get_queryset().filter(id__in=content_ids)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured content"""
        queryset = self.get_queryset().filter(featured=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Mark content as viewed and increment view counter"""
        content = self.get_object()
        
        # Track user progress
        if content.content_type in ['webinar', 'video']:
            progress_data = {
                'content_id': content.id,
                'progress_percentage': 100,  # Assume watched
                'completed': True
            }
            progress_serializer = ContentProgressSerializer(
                data=progress_data, context={'request': request}
            )
            if progress_serializer.is_valid():
                progress_serializer.save()
            
            # Increment view counter
            content.increment_views()
        
        return Response({'status': 'view recorded'})
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Mark template as downloaded and increment counter"""
        content = self.get_object()
        
        if content.content_type == 'template':
            # Increment download counter
            content.increment_downloads()
            
        return Response({'status': 'download recorded'})


class ContentProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for user content progress tracking"""
    serializer_class = ContentProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # The IsAuthenticated permission ensures this is only called by authenticated users
        return ContentProgress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Get all content progress for the current user"""
        progress = self.get_queryset()
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        """Get content that user has started but not completed"""
        progress = self.get_queryset().filter(
            progress_percentage__gt=0,
            progress_percentage__lt=100,
            completed=False
        )
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get content that user has completed"""
        progress = self.get_queryset().filter(completed=True)
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)