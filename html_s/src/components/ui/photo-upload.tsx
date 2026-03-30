'use client';

import React, { useRef, useState, useCallback } from 'react';
import { Camera, X, Upload, Image as ImageIcon, ZoomIn } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PhotoUploadProps {
  photos: string[];
  onChange: (photos: string[]) => void;
  maxPhotos?: number;
  maxSizeMB?: number;
  label?: string;
  disabled?: boolean;
  compact?: boolean;
}

export function PhotoUpload({
  photos,
  onChange,
  maxPhotos = 6,
  maxSizeMB = 10,
  label = 'Фотографии',
  disabled = false,
  compact = false,
}: PhotoUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || disabled) return;
    setError(null);

    const remaining = maxPhotos - photos.length;
    if (remaining <= 0) {
      setError(`Максимум ${maxPhotos} фотографий`);
      return;
    }

    const filesToProcess = Array.from(files).slice(0, remaining);
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];

    filesToProcess.forEach((file) => {
      if (!validTypes.includes(file.type)) {
        setError('Допустимые форматы: JPG, PNG, WebP, GIF');
        return;
      }
      if (file.size > maxSizeMB * 1024 * 1024) {
        setError(`Максимальный размер файла: ${maxSizeMB} МБ`);
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        if (result) {
          onChange([...photos, result]);
        }
      };
      reader.readAsDataURL(file);
    });
  }, [photos, onChange, maxPhotos, maxSizeMB, disabled]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const removePhoto = useCallback((index: number) => {
    onChange(photos.filter((_, i) => i !== index));
  }, [photos, onChange]);

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          {label}
          <span className="text-xs text-slate-400 ml-1.5">({photos.length}/{maxPhotos})</span>
        </label>
      )}

      {/* Drop zone */}
      {photos.length < maxPhotos && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => inputRef.current?.click()}
          className={cn(
            'border-2 border-dashed rounded-xl text-center cursor-pointer transition-all',
            compact ? 'p-4' : 'p-6',
            dragOver
              ? 'border-brand-400 bg-brand-50/50 dark:bg-brand-900/10'
              : 'border-slate-200 dark:border-slate-700 hover:border-brand-300 hover:bg-brand-50/30 dark:hover:bg-brand-900/10',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => {
              handleFiles(e.target.files);
              e.target.value = '';
            }}
            disabled={disabled}
          />
          <div className={cn(
            'rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto mb-2',
            compact ? 'w-10 h-10' : 'w-12 h-12 mb-3'
          )}>
            <Camera size={compact ? 18 : 22} className="text-slate-400" />
          </div>
          <p className={cn(
            'font-medium text-slate-700 dark:text-slate-300',
            compact ? 'text-xs' : 'text-sm'
          )}>
            {dragOver ? 'Отпустите для загрузки' : 'Нажмите или перетащите фотографии'}
          </p>
          <p className="text-xs text-slate-400 mt-1">PNG, JPG, WebP до {maxSizeMB} МБ</p>
        </div>
      )}

      {error && (
        <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
      )}

      {/* Photo grid */}
      {photos.length > 0 && (
        <div className={cn(
          'grid gap-2',
          compact ? 'grid-cols-4' : 'grid-cols-3 sm:grid-cols-4'
        )}>
          {photos.map((photo, i) => (
            <div
              key={i}
              className="relative group aspect-square rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800"
            >
              {photo.startsWith('data:') || photo.startsWith('http') || photo.startsWith('/') ? (
                <img
                  src={photo}
                  alt={`Фото ${i + 1}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <ImageIcon size={20} className="text-slate-400" />
                </div>
              )}

              {/* Overlay */}
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-1.5 opacity-0 group-hover:opacity-100">
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setPreviewUrl(photo); }}
                  className="p-1.5 rounded-lg bg-white/90 text-slate-700 hover:bg-white transition-colors"
                >
                  <ZoomIn size={14} />
                </button>
                {!disabled && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); removePhoto(i); }}
                    className="p-1.5 rounded-lg bg-red-500/90 text-white hover:bg-red-600 transition-colors"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Fullscreen Preview Modal */}
      {previewUrl && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
          onClick={() => setPreviewUrl(null)}
        >
          <button
            onClick={() => setPreviewUrl(null)}
            className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
          >
            <X size={20} />
          </button>
          <img
            src={previewUrl}
            alt="Предпросмотр"
            className="max-w-full max-h-[90vh] rounded-lg object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}

/** Read-only photo gallery for displaying photos */
interface PhotoGalleryProps {
  photos: string[];
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function PhotoGallery({ photos, size = 'md', className }: PhotoGalleryProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  if (!photos || photos.length === 0) return null;

  const sizeClass = size === 'sm' ? 'w-10 h-10' : size === 'md' ? 'w-16 h-16' : 'w-24 h-24';

  return (
    <>
      <div className={cn('flex flex-wrap gap-1.5', className)}>
        {photos.map((photo, i) => (
          <button
            key={i}
            onClick={() => setPreviewUrl(photo)}
            className={cn(
              sizeClass,
              'rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 hover:ring-2 hover:ring-brand-500 transition-all cursor-pointer flex-shrink-0'
            )}
          >
            {photo.startsWith('data:') || photo.startsWith('http') || photo.startsWith('/') ? (
              <img src={photo} alt={`Фото ${i + 1}`} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <ImageIcon size={size === 'sm' ? 12 : 16} className="text-slate-400" />
              </div>
            )}
          </button>
        ))}
      </div>

      {previewUrl && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
          onClick={() => setPreviewUrl(null)}
        >
          <button
            onClick={() => setPreviewUrl(null)}
            className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
          >
            <X size={20} />
          </button>
          <img
            src={previewUrl}
            alt="Предпросмотр"
            className="max-w-full max-h-[90vh] rounded-lg object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
